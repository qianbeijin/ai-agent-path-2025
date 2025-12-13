from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key= os.getenv("DEEPSEEK_API_KEY"), 
    base_url="https://api.deepseek.com"
)

# 1. 创建一个服务员对象
app = FastAPI()

# 2. 定义数据格式 (这是 FastAPI 的强项：类型检查)
# 我们规定：前端发给我的数据，必须包含 text 字段
class TextRequest(BaseModel):
    text: str


# 3. 定义一个接口 (API Endpoint)
# 这是一个 GET 请求，通常用来测试服务活没活着
@app.get("/")
def read_root():
    return {"message": "服务已启动，随时待命！"}

# 4. 定义一个 POST 请求 (这是真正干活的)
# 只有 POST 才能安全地传递大量数据
@app.post("/chat")
def chat_with_ai(request: TextRequest):
    # 这里暂时模拟 AI，等会把你的 DeepSeek 代码搬过来
    system_prompt = request.text
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt}
        ]
    )
    print(response.choices[0].message.content)
    return {"reply": response.choices[0].message.content}

# 注意：这里不需要写 if __name__ == "__main__"...
# 我们是用 uvicorn 命令来启动它的