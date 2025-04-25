# 建议将API密钥存储在环境变量中
import openai
from flask import Blueprint, Response, jsonify, request
AIchat = Blueprint("AIchat", __name__)


OPENROUTER_API_KEY = (
    "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"
)
URL = "http://127.0.0.1:5000"
NAME = "My AI App"

client = openai.OpenAI(
    api_key="sk-keCREBkG2aA9A9222151T3BlBkFJ9C9c498073174fdfae1f",
    base_url="https://aigptx.top/v1/",
)


# Flask 路由，处理主页和表单
@AIchat.route("/chat", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 获取前端传来的问题
        data = request.get_json()
        question = data.get("question")
        print(question)
        history = data.get("history", [])  # 获取历史对话

        if not question:
            return jsonify({"error": "Missing 'question' parameter"})

        # 将历史对话和当前提问整合为新的消息列表
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
        messages.append({"role": "user", "content": question})

        return get_gpt_response(messages)  # ✅ **返回流式响应**


# 调用 GPT 接口的函数
def get_gpt_response(messages):
    try:
        response = client.chat.completions.create(
            model="glm-4-flashx",
            messages=messages,
            stream=True,
        )

        def generate():
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content  # ✅ 逐字输出

        return Response(generate(), mimetype='text/event-stream')  # ✅ **流式返回**

    except openai.OpenAIError as e:
        return Response(f"Error: {str(e)}", content_type="text/plain")
