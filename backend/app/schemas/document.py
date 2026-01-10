# app/schemas/document.py
from pydantic import BaseModel, Field
from typing import List

class UploadResponse(BaseModel):
    status: str = Field("success", description="处理状态")
    message: str = Field(..., description="处理结果详细描述")
    file_name: str = Field(..., description="已上传的文件名")

class DocumentInfo(BaseModel):
    id: str = Field(..., description="文件的唯一ID") # 新增 ID
    name: str = Field(..., description="文件名")
    # 以后可以扩展大小、上传时间等字段

class DocumentListResponse(BaseModel):
    status: str = Field("success")
    data: List[DocumentInfo]