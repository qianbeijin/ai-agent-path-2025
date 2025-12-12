import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载环境变量 (假装我们很专业，不把密码写在代码里)
# 需要在同级目录下建一个名为 .env 的文件，内容写：DEEPSEEK_API_KEY=你的sk-xxxx
load_dotenv()

# 2. 初始化客户端
# 这里的 base_url 是 DeepSeek 的官方接口地址
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), 
    base_url="https://api.deepseek.com"  
)

print("正在呼叫AI...(第一次可能有点慢)")

try:
    response = client.chat.completions.create(
        model= 'deepseek-chat',  #模型名称
        messages=[
            {"role": "system", "content": "你是一个暴躁的程序员助手"},
            {"role": "user", "content": "你好，我刚开始学Python，夸我一句"}
        ],
        stream=False
    )
    # 4. 打印结果
    print("AI 回复：")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"出错了：{e}")