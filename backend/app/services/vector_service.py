# app/services/vector_service.py
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from app.core.config import settings # 引用我们之前建立的配置中心

class VectorService:
    def __init__(self):
        # 从配置中心读取路径，严禁硬编码
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DATA_PATH)
        self.embed_fn = SentenceTransformerEmbeddingFunction(model_name=settings.EMBED_MODEL_PATH)
        self.collection = self.client.get_or_create_collection(
            name="ai_agent_docs",
            embedding_function=self.embed_fn
        )

    def query(self, text: str, n_results: int = 3, doc_id: str = None):
        # 如果传了 doc_id，就构造 ChromaDB 的元数据过滤条件
        # 这里的 "file_id" 必须是你入库时存入 metadata 的 key
        where_filter = {"file_id": doc_id} if doc_id else None
        """纯粹的检索逻辑"""
        return self.collection.query(
            query_texts = [text],
            n_results = n_results,
            where=where_filter,  # 🏆 只有加了这一行，数据库才会真正执行过滤
            include = ["documents", "distances", "metadatas"]
        )

    def add_documents(self, ids, documents, metadatas):
        """纯粹的写入逻辑"""
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def delete_by_source(self, source_name: str):
        """去重逻辑：按来源删除"""
        existing = self.collection.get(where={"source": source_name})
        if existing["ids"]:
            self.collection.delete(where={"source": source_name})

    # app/services/vector_service.py 增加以下方法
    def get_unique_sources(self) -> list:
        """从元数据中提取所有唯一的文件来源"""
        # 获取所有文档的元数据
        results = self.collection.get(include=["metadatas"])
        metadatas = results.get("metadatas", [])
        
        # 使用字典去重，key 是 id
        unique_docs = {}
        for m in metadatas:
            f_id = m.get("file_id")
            if f_id and f_id not in unique_docs:
                unique_docs[f_id] = {
                    "id": f_id,
                    "name": m.get("source") # source 存文件名
                }
        return list(unique_docs.values())