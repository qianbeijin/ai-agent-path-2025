# app/api/v1/document.py
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.document import UploadResponse, DocumentListResponse, DocumentInfo
from app.services.rag_facade import RAGFacade
from app.core.config import settings

router = APIRouter()
rag = RAGFacade()

# 定义临时上传目录，在 config 中配置更好
UPLOAD_DIR = "./temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """获取侧边栏文件列表"""
    # 这里的 sources 应该是一个包含 dict 的 list: [{'id': '...', 'name': '...'}, ...]
    sources = await rag.get_document_list()
    
    # 🏆 修复点：显式从字典中提取字段
    doc_infos = [
        DocumentInfo(id=s['id'], name=s['name']) 
        for s in sources
    ]
    
    return DocumentListResponse(data=doc_infos)

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    上传 PDF 文件并自动触发 RAG 解析入库
    """
    # 1. 安全校验：只允许 PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="目前仅支持 PDF 格式文件")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        # 2. 将上传的文件流保存到本地临时目录
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. 调用 Facade 层进行“解析 -> 切片 -> 入库”全流程
        # 注意：这是我们之前写的异步方法
        result_msg = await rag.ingest_document(file_path)

        return UploadResponse(
            status="success",
            message=result_msg,
            file_name=file.filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
    finally:
        # 4. 无论成功失败，处理完后建议清理临时文件以节省空间
        if os.path.exists(file_path):
            os.remove(file_path)