# test_db.py
import chromadb

# 1. 连接你的数据库（路径必须与 vector_service.py 中一致）
client = chromadb.PersistentClient(path="./chroma_db") 
collection = client.get_collection("ai_agent_docs")

# 2. 打印总数据量
count = collection.count()
print(f"📊 数据库中共有 {count} 条内容块 (Chunks)")

# 3. 抽样检查前 5 条数据的元数据
# 重点检查：是否有 'file_id' 字段，以及它是否与你前端传的 docId 一致
results = collection.get(limit=5)
for i in range(len(results['ids'])):
    print(f"--- Chunk {i} ---")
    print(f"ID: {results['ids'][i]}")
    print(f"Metadata: {results['metadatas'][i]}") # 🏆 这里是精准检索的关键