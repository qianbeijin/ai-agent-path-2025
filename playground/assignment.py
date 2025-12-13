"""
任务：竞品分析助手

场景： 老板想知道“深度求索 (DeepSeek)”和“OpenAI”这两家公司的官网介绍有什么不同。 需求：

程序里定义两个 URL：

URL A: https://www.deepseek.com/ (或者它的关于页面)

URL B: https://openai.com/

分别抓取这两个网页的内容。

写一个 Prompt，让 AI 对比这两段内容，输出一个表格（Markdown 格式），列出两者的异同。

把结果保存到一个叫 report.md 的文件里
"""
 
import os 
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    # 通过os操作在env文件中获取api_key
    api_key = os.getenv("DEEPSEEK_API_KEY"),  
    # 要连接的ai地址
    base_url = "https://api.deepseek.com" 
)

# 抓取网页内容
def get_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("------ 抓取成功！------")
            return response.text[:2000]
        else:
            print(f"抓取失败，错误代码:{response.status_code}")
            return None
    except Exception as e:
        print(f"网络出错了, {e}")
        return None
    
def AI_analysis(url1, url2):
    content1 = get_content(url1)
    content2 = get_content(url2)
    if not (content1 and content2):
        return "获取网页内容失败！" 
    
    # 传递给ai的指令
    system_prompt = """
    你现在是一个商业分析师，我给你两个公司的介绍，你需要对比这两个内容，输出一个Markdown格式的表格，
    列出两者的异同，不需要有多余操作，只需要给我这份表格就行
    """

    # 建立ai连接
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"两段网页内容分别如下：\n第一段：\n{content1}第二段：\n{content2}"}
        ]
    )

    # 返回ai给出的结果
    return response.choices[0].message.content


if __name__ == "__main__":
    url1 = "https://baike.baidu.com/item/%E6%9D%AD%E5%B7%9E%E6%B7%B1%E5%BA%A6%E6%B1%82%E7%B4%A2%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%9F%BA%E7%A1%80%E6%8A%80%E6%9C%AF%E7%A0%94%E7%A9%B6%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8/64541110?fromtitle=DeepSeek&fromid=65258669"
    url2 = "https://baike.baidu.com/item/OpenAI/19758408"
    result = AI_analysis(url1, url2)
    
    # 把字符串存进文件
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(result)

