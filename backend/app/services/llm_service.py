# app/services/llm_service.py
from openai import OpenAI
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )

    async def generate_response_stream(self, messages: list):
        """调用大模型接口（流式返回）"""
        # 1. 开启 stream=True
        response = self.client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            stream=True
        )

        # 2. 异步迭代流式响应
        # 注意：DeepSeek 的 SDK 遵循 OpenAI 规范
        for chunk in response:
            # 3. 提取增量内容（Delta Content）
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                # 4. 实时产生（Yield）每一个 Token
                yield content