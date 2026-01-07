# 【入口】只负责启动和路由分发
from fastapi import FastAPI, HTTPException, UploadFile, File
from schemas import ChatRequest, ChatResponse # 导入契约
from fastapi.middleware.cors import CORSMiddleware
# 👇 2. 引入我们刚才在 services.py 里写的函数
from services import process_pdf_to_db, get_ai_response
import shutil
import os

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

   # 1. 后缀校验
    if not file.filename.endswith(".pdf"):
        # 抛出异常，告诉用户文件类型错误
        raise HTTPException(status_code=400, detail="目前只支持 .pdf 文件")
    
    # 2.临时存储（落盘）
    temp_path = f"temp_{file.filename}"
    try: 
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 3. 调用刚才写的 services 逻辑
        detail = process_pdf_to_db(temp_path)
        return {"status": "success", "message": detail}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
    finally:
        # 4. 毁尸灭迹：无论成功失败，删掉临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
