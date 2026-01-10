import os
import uuid
import logging
from typing import List, Dict, Optional

# 导入你拆分出来的原子化服务
from .vector_service import VectorService
from .document_service import DocumentService
from .llm_service import LLMService

# 配置日志，这是企业级开发的标配
logger = logging.getLogger(__name__)

class RAGFacade:
    def __init__(self):
        """初始化三位一体的核心服务"""
        self.vector_service = VectorService()
        self.doc_service = DocumentService()
        self.llm_service = LLMService()

    async def ingest_document(self, file_path: str) -> str:
        """
        三位一体：解析 -> 清洗 -> 存储 (完全对标 services.py 逻辑)
        """
        try:
            file_name = os.path.basename(file_path)
            
            # 1. 解析与清洗 (调用 DocumentService)
            # 原逻辑：pymupdf 提取并 clean
            full_text = self.doc_service.parse_pdf(file_path)
            
            # 2. 文本切片
            # 原逻辑：500 字符 + 50 重叠
            chunks = self.doc_service.split_text(full_text)
            
            # 3. 去重：按文件名清理旧数据 (调用 VectorService)
            # 原逻辑：collection.get(where={"source": file_name}) 后 delete
            self.vector_service.delete_by_source(file_name)
            
            # 4. 生成 ID 与元数据并存入数据库
            file_uuid = uuid.uuid4().hex[:6]
            ids = [f"{file_name}_{file_uuid}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": file_name, "file_id": file_uuid} for _ in range(len(chunks))]
            
            self.vector_service.add_documents(ids, chunks, metadatas)
            
            logger.info(f"成功解析并入库: {file_name}, 共 {len(chunks)} 块")
            return f"成功解析文件 {file_name}，切分为 {len(chunks)} 块"
            
        except Exception as e:
            logger.error(f"解析文件失败: {file_path}, 错误: {e}")
            raise Exception(f"文档解析入库失败: {str(e)}")

    async def ask_question(self, user_input: str, history: List[Dict]) -> str:
        """
        RAG 核心链路：检索 -> 拼 Prompt -> 调 LLM (完全对标 services.py 逻辑)
        """
        try:
            # 1. 向量检索相关知识
            # 原逻辑：collection.query 拿 n_results=3
            search_results = self.vector_service.query(user_input, n_results=3)
            
            # 2. 阈值过滤与上下文构建
            # 原逻辑：threshold = 0.8
            threshold = 0.8
            filtered_contexts = []
            
            documents = search_results["documents"][0]
            distances = search_results["distances"][0]
            metadatas = search_results["metadatas"][0]
            
            for doc, dist, meta in zip(documents, distances, metadatas):
                if dist < threshold:
                    source = meta.get("source", "未知文档")
                    filtered_contexts.append(f"【来源: {source}】: {doc}")
            
            # 3. 构建动态 Prompt
            context_text = "\n".join(filtered_contexts)
            if not filtered_contexts:
                # 对应 services.py 中的“资料不足”处理逻辑
                prompt = f"由于知识库中没有相关信息，你可以根据你的通用知识回答，但要声明这不是官方答案：{user_input}"
            else:
                # 对应 services.py 中的“约束要求”Prompt
                prompt = f"""你是一个专业、严谨的 AI 助手。请根据以下提供的参考资料回答用户的问题。
                
                ### 约束要求:
                1. 必须优先使用参考资料中的信息。
                2. 如果资料中没有提到相关信息，请诚实告知。
                3. 回答结束后，请务必注明你参考的【来源】文件名。
                
                ### 参考资料:
                {context_text}
                
                ### 用户问题:
                {user_input}
                """

            # 4. 构建消息历史 (拒绝全局变量，使用传入的 history)
            # 核心修正：这里我们只构建本次请求的 messages，不修改外部 history 状态
            messages_to_send = [
                {"role": "system", "content": "你是一个专业、风趣的 AI 助手。请根据你获得的知识内容进行回答。"}
            ] + history + [{"role": "user", "content": prompt}]

            # 5. 调用 LLM 并返回
            return await self.llm_service.generate_response(messages_to_send)

        except Exception as e:
            logger.error(f"问答流程失败: {e}")
            return "抱歉，我断片了，请再说一遍。"
        
    # app/services/rag_facade.py 增加以下方法
    async def get_document_list(self) -> list:
        """获取所有已入库的文档列表"""
        try:
            return self.vector_service.get_unique_sources()
        except Exception as e:
            logger.error(f"获取文档列表失败: {e}")
            return []