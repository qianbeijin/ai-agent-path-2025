# 【入口】只负责启动和路由分发
from fastapi import FastAPI, HTTPException, UploadFile, File
from backend.schemas import ChatRequest, ChatResponse # 导入契约
from fastapi.middleware.cors import CORSMiddleware
# 👇 2. 引入我们刚才在 services.py 里写的函数
from backend.services import add_document_to_db, get_ai_response

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

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    接收前端上传的文件，读取内容，并存入 ChromaDB
    """
    if not file.filename.endswith(".txt"):
        # 抛出异常，告诉用户文件类型错误
        raise HTTPException(status_code=400, detail="目前只支持 .txt 文件")
    
    try:
        # 读取文件 (二进制流)
        # await 是因为读硬盘/网络是慢操作，不能卡住主线程
        content = await file.read()

        # 将文件进行解码操作(Bytes -> String)
        text_content = content.decode("utf-8")

        # services开始干活
        result = add_document_to_db(file.filename, text_content)

        # 给前端返回结果
        return {"filename": file.filename, "status": "success", "detail": result}
    
    except Exception as e:
        print(f"上传失败: {e}")
        # 返回 500 错误码，前端就知道出事了
        raise HTTPException(status_code=500, detail=str(e))
