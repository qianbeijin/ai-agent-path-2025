# app/services/llm_service.py
from openai import OpenAI
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )

    async def generate_response(self, messages: list):
        """调用大模型接口"""
        response = self.client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content