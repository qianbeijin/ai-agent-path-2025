import os
import json # 引入 JSON 库，用来处理数据格式
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# --- 核心任务：做一个翻译器 ---
def ai_translator(text):
    print(f"正在翻译：{text}...")

    # 你的任务：编写一个System Prompt，强制AI只输出JSON，不要废话
    # 这是一个“严厉”的指令
    system_pronpt = """
    你是一个精通八国语言的顶级翻译师，
    用户输入一段中文，你必须严格按照以下JSON格式返回结果：
    {
        "english": "英文翻译",
        "japanese": "日文翻译",
        "sentiment": "情感分析(填: 正向/负向/中性)"
    }
    注意：不要输出 Markdown 代码块，直接输出纯JSON字符串。
    不要说任何多余的话，例如“好的，这是结果”
    """

    try: 
        response = client.chat.completions.create(
            model = "deepseek-chat",
            messages = [
                {"role": "system", "content": system_pronpt},
                {"role": "user", "content": text}
            ],
            stream = False
        )

        # 获取 AI 的回答
        result = response.choices[0].message.content
        
        # 尝试把它解析成 Python 字典，验证是不是标准 JSON
        data = json.loads(result)
        return data
    
    except json.JSONDecodeError:
        print("错误：AI没有返回有效的JSON格式。")
        print(f"AI的原始回答是：{result}")
        return None
    except Exception as e:
        print(f"API 出错：{e}")
        return None
    

if __name__ == "__main__":
    text = "我今天心情很好，因为我学会了使用新的AI工具！"
    translation = ai_translator(text)
    if translation:
        print("\n------ 翻译成功 ------")
        print(f"英文: {translation['english']}")
        print(f"日文: {translation['japanese']}")
        print(f"情感: {translation['sentiment']}")
        print("----------------------")