# app/api/v1/chat.py
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse # 导入刚才定义的模型
from app.services.rag_facade import RAGFacade

router = APIRouter()
rag = RAGFacade()

@router.post("/send", response_model=ChatResponse) # 强制要求返回符合 ChatResponse 格式的数据
async def chat_endpoint(request: ChatRequest):
    """
    接收标准化的 ChatRequest，返回标准化的 ChatResponse
    """
    # 核心：将 Pydantic 对象转为 RAGFacade 需要的原始类型
    history_data = [m.model_dump() for m in request.history]
    
    # 执行业务逻辑
    ai_answer = await rag.ask_question(request.message, history_data)
    
    # 按照 Schema 结构返回数据
    return ChatResponse(
        status="success",
        answer=ai_answer,
        sources=[] # 这里以后可以对接真正的来源数据
    )