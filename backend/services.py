import uuid
import chromadb
import re
import pymupdf
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 1. 基础配置 (路径建议使用绝对路径或基于项目根目录的相对路径)
CHROMA_DATA_PATH = "./chroma_db"
# 模型地址
EMBED_MODEL_PAHT = "D:/models/all-MiniLM-L6-v2"

try:
    # 初始化数据连接
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    # 初始化模型
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL_PAHT)
except Exception as e:
    print("数据库连接失败或模型加载失败！")
    
# 创建书架
collection = client.get_or_create_collection(
    name = "ai_agent_docs",
    embedding_function = embedding_fn
)

# 清洗数据的函数
def clean(text: str) -> str:
    """最严格的 RAG 清洗逻辑"""
    # 1.先合并所有空白字符
    text = re.sub(r"\s+", " ", text)
    # 2. 剔除 PDF 页码干扰 (12 | Page)
    text = re.sub(r"\s*\d+\s*\|\s*Page", "", text)
    # 3. 剔除方括号引用 [12] (保留文字，删掉引用符号)
    text = re.sub(r"\s*\[\d+\]\s*", "", text)
    # 返回字符串内容
    return text

def process_pdf_to_db(file_path: str):
    """三位一体：解析 -> 清洗 -> 存储 (带去重)"""
    file_name = os.path.basename(file_path)

    # --- 核心：去重逻辑 ---
    # 检查数据库中是否已存在该文件，如果存在则先删除
    existing = collection.get(where={"source": file_name})
    if existing["ids"]:
        collection.delete(where={"source": file_name})
        print(f"检测到旧记录，已清理: {file_name}")

    # --- 提取与清洗 ---
    doc = pymupdf.open(file_path)
    full_text = ""
    for page in doc: 
        full_text += page.get_text() + "\n"
    # 释放资源
    doc.close()

    # 数据清洗
    full_text = clean(full_text)

    # 切片与入库
    chunk_size = 500
    overlap = 50
    start = 0
    chunks = []
    while start < len(full_text):
        chunks.append(full_text[start:start+chunk_size])
        start = start+chunk_size-overlap

    # 生成带 UUID 的 ID 组，防止全球唯一性冲突
    file_uuid = uuid.uuid4().hex[:6]
    ids = [f"{file_name}_{file_uuid}_{i}" for i in range(len(chunks))]
    # 存入元数据，方便以后根据 source 字段进行过滤或删除
    metadatas = [{"source": file_name} for _ in range(len(chunks))]

    collection.add(
        documents = chunks,
        ids = ids,
        metadatas= metadatas
    )
    
    return f"成功解析文件 {file_name}，切分为 {len(chunks)} 块"

# 建立与 AI 的连接
ai_collect = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = "https://api.deepseek.com"
)

memory_history = [
    { "role": "system", "content": "你是一个专业、风趣的 AI 助手。请根据你获得的知识内容进行回答。" } 
]

# 逻辑：搜数据库 -> 拿结果 -> 拼 Prompt -> 调 DeepSeek -> 存记忆
def get_ai_response(user_input: str) -> str:

    # 去数据库里检索相关的知识
    # 这一步会调用你的 collection 把问题也变成向量，然后去比对
    similar_results = collection.query(
        query_texts = [user_input],
        n_results = 3,
        include = ["documents", "distances", "metadatas"]
    )

    # 获取相关内容和相似度
    text_results = similar_results["documents"][0]
    distances_results = similar_results["distances"][0]
    metadatas = similar_results["metadatas"][0]

    # 设置阈值
    threshold = 0.8
    filtered_results = []
    for i in range(len(text_results)):
        if distances_results[i] < threshold:
            # 这里的格式是为了让 AI 知道来源
            source = metadatas[i].get("source", "未知文档")
            filtered_results.append(f"【来源: {source}】: {text_results[i]}")
    
    # 动态构建 Prompt
    if not filtered_results:
        current_prompt = f"由于知识库中没有相关信息，你可以根据你的通用知识回答，但要声明这不是官方答案：{user_input}"
    else:
        context_text = "\n".join(filtered_results)
        # 重点优化：增加角色约束和回答结构
        current_prompt = f"""你是一个专业、严谨的 AI 助手。请根据以下提供的参考资料回答用户的问题。
        
        ### 约束要求:
        1. 必须优先使用参考资料中的信息。
        2. 如果资料中没有提到相关信息，请诚实告知。
        3. 回答结束后，请务必注明你参考的【来源】文件名。
        
        ### 参考资料:
        {context_text}
        
        ### 用户问题:
        {user_input}
        """

    # 提问的时候可以将获取到的知识库内容告诉AI，但是在存储历史对话的时候只需要将用户的提问和AI的回答存入即可
    # 这样可以保证历史记录的整洁
    messages_to_send = memory_history.append({"role": "user", "content": current_prompt})

    # 获取 AI 的回复
    try:
        response = ai_collect.chat.completions.create(
            model = 'deepseek-chat',
            messages = messages_to_send,
            stream = False
        )
        ai_answer = response.choices[0].message.content

        # 存入历史对话中
        memory_history.append({"role": "user", "content": user_input})
        memory_history.append({"role": "assistant", "content": ai_answer})
        return ai_answer
    except Exception as e:
        print(f"DeepSeek 调用失败: {e}")
        return "抱歉，我断片了，请再说一遍。"

    




