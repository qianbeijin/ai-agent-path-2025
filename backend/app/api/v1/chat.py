# app/api/v1/chat.py
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse # 导入刚才定义的模型
from app.services.rag_facade import RAGFacade
from fastapi.responses import StreamingResponse
import json

router = APIRouter()
rag = RAGFacade()

@router.post("/send", response_model=ChatResponse) # 强制要求返回符合 ChatResponse 格式的数据
async def chat_endpoint(request: ChatRequest):
    """
    接收标准化的 ChatRequest，返回标准化的 ChatResponse
    """
    # 核心：将 Pydantic 对象转为 RAGFacade 需要的原始类型
    history_data = [m.model_dump() for m in request.history]

    # 定义一个生成器，将AI的回答逐字弹出
    async def event_generator():
        async for chunk in rag.ask_question_stream(
            request.message, 
            history_data, 
            doc_id=request.docId
        ):
            # 必须符合 SSE 格式：data: 内容\n\n
            yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n" # 传输结束标志
            
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")