# 1. 导入必要的库 (OpenAI, ChromaDB, SentenceTransformer 等)
import os
from openai import OpenAI
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量到当前运行环境中
# 例如：将文件中的 API_KEY=xxx 转为 os.environ["API_KEY"] = "xxx"
load_dotenv()

# 2. 初始化模型
# 使用的是本地模型
model_name = "D:/models/all-MiniLM-L6-v2"
try:
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name = model_name)
except Exception as e:
    print("模型加载失败！")


# 3. 初始化数据库连接和 Collection (书架)

# 初始化数据连接
client = chromadb.PersistentClient(path="./chroma_db")

# 创建书架
collection = client.get_or_create_collection(
    name = "first_collection",
    embedding_function = embedding_fn
)

#    - 需要实现 embed_query (给查询用)

#    - 需要实现 embed_documents (给存文档用)

# 4. 编写 add_document_to_db 函数
#    - 逻辑：读内容 -> 切分 -> 生成 ID -> 存入
def add_document_to_db(file_name: str, content: str):
    if not content:
        print("文件处理失败或文件为空")
        return
    
    # 将文件内容按行进行分割，同时舍弃空行
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    # 生成id
    ids = [f"{file_name}_{index}" for index in range(len(lines))]
    print(lines)

    # 存入书架中
    try:
        collection.add(
            documents = lines,
            ids = ids
        )
        return f"成功存入了{len(lines)}行"
    except Exception as e:
        print(f"❌ ChromaDB 入库失败: {e}")
        # 抛出异常，让 main.py 知道出事了，从而返回 500 给前端
        raise e

# 5. 编写 get_ai_response 函数
#    - 逻辑：搜数据库 -> 拿结果 -> 拼 Prompt -> 调 DeepSeek -> 存记忆
memory_history = [
    # 保持 system prompt 简洁，我们稍后会用 RAG 动态添加 context
    {"role": "system", "content": "你是一个专业、风趣的 AI 助手。请根据你获得的知识内容进行回答，如果知识中没有，则随机应变。"}
]

ai_collect = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = "https://api.deepseek.com"
)

def get_ai_response(user_input: str):

    # 去数据库里检索相关的知识
    # 这一步会调用你的 collection 把问题也变成向量，然后去比对
    similar_results = collection.query(
        query_texts = [user_input],
        n_results = 3   # 返回最相似的三条结果
    )

    # 获取文字内容
    text_results = similar_results["documents"][0]

    # 拼接prompt
    prompt = f"以下是参考的公司知识库内容：\n{text_results}\n\n请参考以上内容回答我的问题：{user_input}"
    # 将对话内容存入历史对话列表中
    memory_history.append({"role": "user", "content": prompt})


    try: 
        # 获取AI的回复
        response = ai_collect.chat.completions.create(
            model = "deepseek-chat",
            messages = memory_history,
            stream = False 
        )
        # 获取AI回复的文本内容
        ai_answer = response.choices[0].message.content
        # 把ai的回复也添加进入对话历史中，便于ai可以联系上下文
        memory_history.append({"role": "assistant", "content": ai_answer})
        return ai_answer
    except Exception as e:
        print(f"DeepSeek 调用失败: {e}")
        return "抱歉，我断片了，请再说一遍。"







