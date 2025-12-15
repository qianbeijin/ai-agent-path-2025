# 【入口】只负责启动和路由分发
from fastapi import FastAPI
from backend.schemas import ChatRequest, ChatResponse # 导入契约
from backend.services import get_ai_response        # 导入大脑

app = FastAPI(title="AI Agent Backend", version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Agent Backend")

# --- 新增的代码开始 ---
# 允许跨域请求（解决前端 5173 访问 8000 端口被浏览器拦截的问题）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境要改成具体的域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许 GET, POST, OPTIONS 等所有方法
    allow_headers=["*"],  # 允许所有 Header
)

@app.get("/")
def health_check():
    return {"status": "running", "message": "Backend is online!"}

# 注意：response_model=ChatResponse 是关键
# 它告诉 FastAPI：必须严格按照我们在 schemas 里定义的格式返回，多一个字段都不行
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    
    # 1. 拿到数据 (已经经过 Pydantic 验证了，肯定是 str)
    user_input = request.message
    
    # 2. 调用业务逻辑
    ai_reply = get_ai_response(user_input)
    
    # 3. 组装返回 (情感分析暂时写死，后面再接逻辑)
    return ChatResponse(
        reply=ai_reply,
        sentiment="neutral" 
    )