# app/services/document_service.py
import pymupdf
import re
import uuid
import os

class DocumentService:
    @staticmethod
    def clean_text(text: str) -> str:
        """从原有逻辑迁移过来的清洗函数"""
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\s*\d+\s*\|\s*Page", "", text)
        return text.strip()

    def split_text(self, text: str, chunk_size: int = 500, overlap: int = 50):
        """切片逻辑"""
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start:start + chunk_size])
            start = start + chunk_size - overlap
        return chunks

    def parse_pdf(self, file_path: str):
        """解析逻辑"""
        doc = pymupdf.open(file_path)
        full_text = self.clean_text("".join([page.get_text() for page in doc]))
        print(full_text)
        doc.close()
        return full_text