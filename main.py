import os
import requests # 👈 主角登场：它是用来上网的
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), 
    base_url="https://api.deepseek.com"
)

# --- 工具函数：去网上抓取文字 ---
def fetch_web_content(url):
    print(f"正在抓取网页: {url} ...")
    try:
        # 1. 发送 GET 请求 (就像你在浏览器地址栏敲回车)
        response = requests.get(url, timeout=10)
        
        # 2. 检查状态码 (200 代表成功，404 代表没找到)
        if response.status_code == 200:
            print("抓取成功！")
            # 只取前 2000 个字，防止文章太长超过 AI 限制
            return response.text[:2000] 
        else:
            print(f"抓取失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        print(f"网络出错了：{e}")
        return None

# --- 核心逻辑：抓取 + 总结 ---
def ai_summarizer(url):
    # 第一步：用 requests 拿到数据
    content = fetch_web_content(url)
    
    if not content:
        return "无法获取网页内容。"

    # 第二步：把数据喂给 AI
    system_prompt = """
    你是一个信息摘要助手。
    请阅读用户提供的网页源代码/文本，用一句简练的话总结这个网页是干什么的。
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"网页内容如下：\n{content}"}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # 我们拿 Python 官网的“关于”页面做测试
    target_url = "https://peps.python.org/pep-0020/" 
    # (这是著名的《Python之禅》页面)
    
    summary = ai_summarizer(target_url)
    print("\n------ AI 总结结果 ------")
    print(summary)
    print("-------------------------")