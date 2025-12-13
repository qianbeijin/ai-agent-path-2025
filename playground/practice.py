import os  # 导入操作系统相关功能模块
from openai import OpenAI
from dotenv import load_dotenv
import requests  # 导入网络工具包

load_dotenv()

client = OpenAI(
    # 通过os操作在env文件中获取api_key
    api_key = os.getenv("DEEPSEEK_API_KEY"),  
    # 要连接的ai地址
    base_url = "https://api.deepseek.com" 
)

def fetch_web_content(url):
    print(f"正在抓取{url}的内容...")
    # 捕获可能出现的异常
    try:
        # 向该接口发送get请求，并且设置超时时间
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # 使用切片方法限制返回字数，防止字数超过 AI 提问上限
            print("抓取成功！")
            return response.text[:200]
        else:
            print(f"内容抓取失败，状态码为：{response.status_code}")
            return None
    except Exception as e:
        print(f"网络出错了：{e}")
        return None
    
def askAI(url):
    url_content = fetch_web_content(url)
    if not url_content:
        print("无法获取网页内容")
        return 
    
    system_prompt = """
    你现在是一位内容总结大师，我需要你把用户输入的内容总结为一句精简干练的话，
    不需要有多余的回答
    """

    response = client.chat.completions.create(
        # 选取 AI 模型
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"网页内容如下：\n{url_content}"}
        ]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    # 这是需要获取内容的网页接口
    target_url = "https://peps.python.org/pep-0020/" 
    summary = askAI(target_url)
    print("\n------ AI 总结结果 ------")
    print(summary)
    print("-------------------------")