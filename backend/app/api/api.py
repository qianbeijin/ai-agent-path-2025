# app/api/api.py
from fastapi import APIRouter
from app.api.v1 import chat,document # 导入你的 v1 模块

api_router = APIRouter()
# 挂载 chat 模块，并指定前缀
api_router.include_router(chat.router, prefix="/v1/chat", tags=["Chat"])
# 挂载 document 模块，并指定前缀
api_router.include_router(document.router, prefix="/v1/document", tags=["Document"])