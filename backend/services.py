# 【业务逻辑】真正干活的大脑 (DeepSeek 调用)
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 初始化客户端 (单例模式：整个程序只初始化一次)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def get_ai_response(user_text: str) -> str:
    """
    专门负责调用 AI 的业务逻辑函数
    """
    print(f"正在处理业务逻辑: {user_text}")
    
    try:
        # 这里用简单的对话模式，后面我们会升级成 RAG
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业、严谨的 AI 助手。"},
                {"role": "user", "content": user_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"DeepSeek 调用失败: {e}")
        return "抱歉，AI 大脑暂时掉线了，请稍后再试。"