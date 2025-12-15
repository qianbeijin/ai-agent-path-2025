#【数据标准】定义输入输出的“契约” (Pydantic)
from pydantic import BaseModel, Field

# 定义用户发送的数据格式
class ChatRequest(BaseModel):
    # Field 用来描述这个字段，方便生成文档
    message: str = Field(..., description="用户输入的聊天内容", example="DeepSeek 是哪家公司的？")


# 定义我们返回给前端的数据格式
class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI 的回复内容")
    sentiment: str = Field(default="neutral", description="情感分析结果")