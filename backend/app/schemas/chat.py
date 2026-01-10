# app/schemas/chat.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    """单条消息模型"""
    role: str = Field(..., description="角色: user 或 assistant")
    content: str = Field(..., description="消息内容")

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户当前提问")
    history: List[Message] = Field(default=[], description="对话历史上下文")
    # 🏆 核心补丁：增加可选的文档 ID
    docId: Optional[str] = Field(default=None, description="选中的文档 ID，用于精准 RAG")

class ChatResponse(BaseModel):
    """标准 API 响应模型"""
    status: str = Field("success", description="状态码")
    answer: str = Field(..., description="AI 生成的回答内容")
    # 以后可以扩展，比如返回本次消耗的 Token 数或检索到的来源
    sources: Optional[List[str]] = Field(None, description="参考文档来源列表")