# Project: testai

學習 AI 的實驗 repo。以小範例、可拋棄的 prototype 為主。

## 溝通風格（重要）
- 使用者**不是工程師**，請用白話中文
- 英文術語要附白話說明，例如「commit（把改動存檔）」
- 不要假設使用者懂指令或流程名詞
- 給步驟前先說「為什麼要做」和「做完會怎樣」
- 一次只引導一步，不要一口氣給很多動作
- 答案優先給「下一步該打什麼」，再給原理
- 回答我問題時，先給結論再給解釋

## Stack
<!-- 確定後補上即可，先留空 -->
- Language: Python (預設)
- Package manager: uv / pip
- AI SDK: Anthropic / OpenAI（依範例）
- Test: pytest（必要時才加）

## Commands
<!-- 補上實際指令 -->
- run:   `python <script>.py`
- test:  `pytest`
- lint:  `ruff check .`

## Conventions
- 檔案命名：snake_case
- 不寫註解，除非是非顯而易見的 WHY
- 學習用範例放 `examples/`，實驗放 `experiments/`
- 一個範例 = 一個檔案，避免過早抽象

## Don'ts
- 不要安裝新套件前不問我
- 不要為了「完整性」加 try/except 包住一切
- 不要產生 *.md 文件除非我要
- 不要把 prototype 重構成「production-ready」架構

## Security Rules

### Secrets
- API key 一律走 `os.environ`，禁止 hardcode
- `.env*` 永不 commit；新增環境變數時同步更新 `.env.example`
- 看到疑似 token / API key 出現在 diff，立刻停下來警告我
- 範例程式碼貼出來前，先檢查有沒有夾帶我本機的 key

### AI / LLM 特有風險
- 呼叫 LLM 時把使用者輸入當「不可信資料」處理，不要直接餵進 system prompt
- 不要把 LLM 回傳內容直接 `eval()` / `exec()` / shell execute
- 範例若涉及 tool use / function calling，工具的副作用要明確（不要讓 LLM 直接刪檔、發網路請求到任意網址）
- prompt 裡若有 `{user_input}` 插值，標註清楚哪段是不可信來源

### Boundaries
- 任何外部輸入（檔案、網路、CLI 參數）進來先驗證型別
- 子程序呼叫用 list 形式（`subprocess.run([...])`），禁止 `shell=True` + 字串拼接

### Refuse to do
- 不要 `--no-verify` 跳過 pre-commit hook
- 不要為了讓範例跑起來而停用 SSL 驗證
- 不要把測試用的 dummy key 寫成看起來像真 key 的格式

## Current Focus
<!-- 每隔幾週手動更新一次 -->
- 目前在熟悉 Claude Code 的記憶與對話結構
