# 【业务逻辑】真正干活的大脑 (DeepSeek 调用)
import os
from openai import OpenAI
from dotenv import load_dotenv
import chromadb # 新增：引入 ChromaDB
# 👇 直接引入原厂引擎，不再用 chromadb.utils 里的那个了
from sentence_transformers import SentenceTransformer
from typing import List

load_dotenv()

# --- 1. 定义适配器（转接头） ---
class MyLocalEmbeddingFunction:
    def __init__(self, model_path):
        # 内部加载真正的模型
        self.model = SentenceTransformer(model_path)
        # 给模型起个名字，满足 ChromaDB 的“虚荣心”

    def name(self):  # ← 没有 @property，没有 self.name = ...，就是普通方法！
        return "my_local_model"
    
    # 1. 对接 query() 接口
    def embed_query(self, input: str) -> List[float]:
        return self.model.encode(input).tolist()

    # 2. 对接 add() 接口
    def embed_documents(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input).tolist()

    # 3. 保底方案：有些版本直接调用对象本身
    def __call__(self, input):
        # 当 ChromaDB 调用它时，它负责把文字转成向量列表
        return self.model.encode(input).tolist()

# --- 2. 你的本地路径 ---
local_model_path = "D:/models/all-MiniLM-L6-v2"

# --- 3. 初始化（通过转接头初始化） ---
try:
    # 这一步非常关键：要把路径传给类，而不是直接给 SentenceTransformer
    custom_ef = MyLocalEmbeddingFunction(model_path=local_model_path)
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    raise e

# --- 4. 连接数据库 ---
from pathlib import Path
# 获取当前文件所在目录（backend/）
CURRENT_DIR = Path(__file__).parent
# 指向与 backend 同级的 chroma_db
CHROMA_PATH = CURRENT_DIR.parent / "chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

knowledge_collection = chroma_client.get_or_create_collection(
    name = "company_knowledge", 
    embedding_function = custom_ef 
)

# 这是一个简易的内存数据库，用来存聊天记录 (短期记忆)
memory_store = [
    # 保持 system prompt 简洁，我们稍后会用 RAG 动态添加 context
    {"role": "system", "content": "你是一个专业、风趣的 AI 助手。请根据你获得的知识内容进行回答，如果知识中没有，则回答‘我无法从公司知识库中找到相关信息’。"}
]

# 初始化客户端 (单例模式：整个程序只初始化一次)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def get_ai_response(user_text: str) -> str:
    """
    专门负责调用 AI 的业务逻辑函数
    """
    print(f"正在处理业务逻辑: {user_text}")

    # 1. 🔍 【新增】去数据库里检索相关的知识
    # 这一步会调用你的 custom_ef 把问题也变成向量，然后去比对
    results = knowledge_collection.query(
        query_texts = [user_text],
        n_results = 3  # 找最相关的 3 条
    )

    # 提取搜索到的文字内容
    retrieved_docs = results['documents'][0]
    context = "\n".join(retrieved_docs)
    print(f"找到的相关知识: {context}")

    # 2. 📝 【新增】把搜到的知识塞进 Prompt 里，喂给 DeepSeek
    # 我们构造一个增强后的 Prompt
    enriched_prompt = f"以下是参考的公司知识库内容：\n{context}\n\n请根据以上内容回答用户的问题：{user_text}"

    # 将用户的问题存入记忆（使用增强后的内容）
    memory_store.append({"role": "user", "content": enriched_prompt})
    
    try:
        # 这里用简单的对话模式，后面我们会升级成 RAG
        response = client.chat.completions.create(
            model = "deepseek-chat",
            messages = memory_store,  # 关键修改：把祖宗十八代的聊天记录都发过去
            stream = False
        )
        ai_answer = response.choices[0].message.content
        memory_store.append({"role": "assistant", "content": ai_answer})
        return ai_answer
    except Exception as e:
        print(f"DeepSeek 调用失败: {e}")
        return "抱歉，我断片了，请再说一遍。"
    

# 将上传的文件内容进行拆分，然后存进db仓库
def add_document_to_db(file_name: str, text_content: str):

    """
    接收文件名和文本内容，将其处理并存入 ChromaDB
    参数:
        filename: 文件名 (用于生成唯一ID，防止冲突)
        text_content: 文件内的纯文本
    """
    print(f"📄 正在处理上传文件: {file_name}...")

    # 将内容按行进行拆分
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]

    if not lines:
        print(f'{file_name}文件为空')
        return "空文件"

    # 将每一行内容添加专属id（不是必须，但是建议）
    ids = [f"{file_name}_{index}" for index in range(len(lines))]
    print("✅文件处理成功！")
    try:

        # 将内容添加进知识仓库存储
        knowledge_collection.add(
            documents = lines,
            ids = ids
        )

        return f"成功存入了{len(lines)}行"

    except Exception as e:
        print(f"❌ ChromaDB 入库失败: {e}")
        # 抛出异常，让 main.py 知道出事了，从而返回 500 给前端
        raise e