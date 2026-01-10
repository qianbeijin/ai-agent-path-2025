import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    """全局配置中心：所有硬编码的终点"""
    # AI 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    # 路径配置
    CHROMA_DATA_PATH: str = os.getenv("CHROMA_DATA_PATH", "./chroma_db")
    EMBED_MODEL_PATH: str = os.getenv("EMBED_MODEL_PATH", "D:/models/all-MiniLM-L6-v2")
    
    # RAG 参数配置
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 50))
    RETRIEVAL_TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.8

# 实例化
settings = Settings()