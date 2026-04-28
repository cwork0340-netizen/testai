"""
Stage 1: Hello Agent
你的第一個會講話的 AI agent。

跑法：
    cd agent
    pip install -r requirements.txt
    python hello.py
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# 從 .env 讀取 API key（不會把 key 寫進程式碼）
load_dotenv()

# 建立 Anthropic 客戶端 — 這是跟 Claude 講話的窗口
client = Anthropic()

# 你想問 Claude 的話
question = "用三句話告訴我：什麼是 AI agent？跟一般的 chatbot 有什麼不同？"

# 送出 request → 收到 response
response = client.messages.create(
    model="claude-opus-4-7",   # 用 Anthropic 最新最強的模型
    max_tokens=1024,            # 回覆最多 1024 個 token（夠了）
    messages=[
        {"role": "user", "content": question},
    ],
)

# Claude 的回覆藏在 response.content 裡（可能有多個 block）
print(f"我問：{question}\n")
print("Claude 答：")
for block in response.content:
    if block.type == "text":
        print(block.text)

# 順便看一下用了多少 token（之後會用來估成本）
print(f"\n--- 這次用量 ---")
print(f"輸入 token：{response.usage.input_tokens}")
print(f"輸出 token：{response.usage.output_tokens}")
