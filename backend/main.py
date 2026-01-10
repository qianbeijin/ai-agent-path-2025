import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 1. 导入配置中心和路由汇总
from app.core.config import settings
from app.api.api import api_router

# 2. 定义生命周期管理 (Lifespan)
# 30k 标准：在应用启动时初始化数据库连接，关闭时优雅释放资源
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动逻辑：比如打印模型加载路径
    print(f"--- 正在从 {settings.EMBED_MODEL_PATH} 加载 Embedding 模型 ---")
    yield
    # 应用关闭逻辑
    print("--- 正在关闭 AI 服务并清理资源 ---")

# 3. 初始化 FastAPI 实例
app = FastAPI(
    title="Gemini-Style RAG AI Agent",
    description="企业级 RAG 智能体后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 4. 配置企业级 CORS (跨域资源共享)
# 严禁直接写 ["*"]，应通过 .env 配置允许的来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 你的 Vue 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. 挂载版本化路由汇总
# 所有的接口现在都统一通过 /api 访问
app.include_router(api_router, prefix="/api")

# 6. 入口执行
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True  # 开发模式下开启热更新
    )