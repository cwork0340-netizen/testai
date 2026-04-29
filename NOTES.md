# Claude Code 速查表

我的個人筆記，方便日後翻查。

## 只要記 6 個指令

| 指令 | 用途 |
|---|---|
| `/clear` | 清空對話。換主題前打一次，省 Token。 |
| `/help` | 列出所有指令 |
| `#` | 把後面那句話存進 CLAUDE.md（會問存到哪） |
| `@` | 引用檔案，例如 `@README.md` |
| `Esc` | 打斷 Claude |
| `Esc Esc` | 編輯上一則訊息 |

## 最常用的兩個：`#` 和 `@`

### `#` — 快速新增記憶
```
# 不要用 try/except 包整個函式
```
Claude 會問存到專案還是全域，選完自動寫進 CLAUDE.md。

### `@` — 引用檔案
```
@CLAUDE.md 幫我看哪些規則太囉嗦
```

## 其他事情：用中文講就好

| 想做什麼 | 直接打 |
|---|---|
| 換分支 | 「切到 main 分支」 |
| 跑測試 | 「跑測試」 |
| 看改動 | 「看一下 git diff」 |
| 提交 | 「commit 這些改動，訊息用中文」 |
| 推遠端 | 「push 上去」 |
| 找程式碼 | 「找 login 相關的檔案」 |
| 看檔案 | `@檔名` 或「打開 X」 |
| 評估風險 | 「這樣改有什麼風險？」 |

## 典型工作流程

```
你: @CLAUDE.md 幫我加 Anthropic API hello world 範例
Claude: <寫程式>
你: 跑跑看
Claude: <跑> 結果...
你: 好，commit 一下
Claude: <commit>
你: /clear     ← 任務結束清空，準備下一個
```

## 三個關鍵習慣

1. **`/clear` 切換任務** — 不同功能開新對話，避免 context 越拉越長。
2. **明確指出檔案路徑** — 與其讓 Claude 搜尋，不如直接 `@檔名` 或說「改 src/auth/login.py:42」，省一輪查找。
3. **全域偏好寫一次** — 通用 coding style 寫在 `~/.claude/CLAUDE.md`，所有專案共用。

## 記憶檔案分工

| 檔案 | 用途 |
|---|---|
| `CLAUDE.md`（專案根目錄） | 此專案的 Stack / Commands / Conventions / Security |
| `~/.claude/CLAUDE.md`（全域） | 你的個人偏好（語言、coding style） |
| `.claude/settings.json` | 工具權限白名單，減少 y/n 詢問 |
| `NOTES.md`（本檔） | 個人筆記、速查表 |
