# LINE 相片整理工具

把 LINE 群組裡的照片拖進視窗，填好「日期 + 群組 + 活動」，自動改檔名、分類、上傳到 Google 雲端硬碟，並把分享連結複製到剪貼簿，可以直接貼回 LINE 群組。

## 它解決什麼

行政流程裡常見的：照片散落在 LINE 群組 → 要一張張另存 → 改檔名 → 分類 → 上傳到雲端 → 通知大家。這支工具把「另存之後」的所有步驟自動化。

- ✅ 拖曳一次處理幾十張照片
- ✅ 自動依「群組 / 日期_活動」分資料夾
- ✅ 自動改檔名（例：`2026-05-21_2025全瑩TWBIO_大群_年終尾牙_001.jpg`）
- ✅ 自動產生分享連結並複製到剪貼簿
- ✅ 群組清單可自己增減，下次打開還在

---

## 第一次安裝（Windows）

### 1. 安裝 Python 3.10 以上版本

到 <https://www.python.org/downloads/windows/> 下載最新的 Python 安裝檔。

⚠️ 安裝時**務必勾選**「Add Python to PATH」這個選項，不然之後指令會找不到。

### 2. 下載這個專案

兩種方式擇一：

- **方式 A（推薦）**：用 GitHub Desktop 或 `git clone` 把這個 repo 抓下來
- **方式 B**：在 GitHub 頁面點「Code → Download ZIP」解壓縮

### 3. 安裝相依套件

打開「命令提示字元」（按 Windows 鍵打 `cmd`），切換到專案資料夾，執行：

```bat
pip install -r requirements.txt
```

### 4. 取得 Google Drive API 金鑰（最麻煩，但只要做一次）

這一步是讓你的程式可以代你寫入你的 Google 雲端硬碟。

1. 到 <https://console.cloud.google.com/> 用你的 Google 帳號登入
2. 建立一個新專案（名字隨意,例如 `line-photo`）
3. 左側選單 → 「API 和服務」→「程式庫」→ 搜尋 **Google Drive API** → 點「啟用」
4. 左側選單 → 「API 和服務」→「OAuth 同意畫面」
   - User Type 選 **External（外部）** → 建立
   - App name 隨便填、User support email 選你自己的 email、Developer contact 填你自己的 email → 儲存
   - **Test users**（測試使用者）那一頁,把你自己的 Google email 加進去 → 儲存
5. 左側選單 → 「API 和服務」→「憑證」→ 點「建立憑證」→「OAuth 用戶端 ID」
   - 應用程式類型選 **桌面應用程式**
   - 名稱隨意 → 建立
6. 建好之後會彈出對話框,點「下載 JSON」
7. 把下載的檔案改名成 **`credentials.json`**,放到這個專案的資料夾裡（跟 `main.py` 同一層）

### 5. 第一次執行

在專案資料夾打開命令提示字元,執行：

```bat
python main.py
```

第一次跑會自動跳出瀏覽器讓你授權 Google 帳號。授權完之後它會在資料夾產生 `token.json`,之後就不會再問了。

---

## 日常使用流程

1. 雙擊 `main.py`(或在命令列 `python main.py`)開啟視窗
2. 在 LINE 群組裡：
   - 點第一張照片 → **Shift + 點最後一張**(一次全選範圍)
   - 直接把照片**拖進視窗**
3. 在視窗裡填寫：
   - **日期**：預設今天,要改就點日曆
   - **群組**：從下拉選單選；沒有就按「＋ 新增群組」
   - **活動**：例如「年終尾牙」、「5 月例會」
4. 按 **📤 上傳**
5. 跳出「上傳完成」視窗,連結已經在剪貼簿 → 切回 LINE 直接 Ctrl+V 貼上

### 雲端的資料夾結構長這樣

```
line 照片/
└── 2025全瑩TWBIO_大群/
    ├── 2026-05-21_年終尾牙/
    │   ├── 2026-05-21_2025全瑩TWBIO_大群_年終尾牙_001.jpg
    │   ├── 2026-05-21_2025全瑩TWBIO_大群_年終尾牙_002.jpg
    │   └── ...
    └── 2026-05-15_5月例會/
        └── ...
```

---

## 設定檔(`config.json`)

| 欄位 | 說明 |
|---|---|
| `drive_root_folder` | 雲端硬碟根資料夾名稱(目前是 `line 照片`) |
| `groups` | 群組下拉選單的選項；按「＋ 新增群組」會自動寫進來 |
| `filename_pattern` | 檔名格式,可用 `{date}` `{group}` `{activity}` `{seq:03d}` |
| `date_format` | 日期顯示格式,預設 `%Y-%m-%d` |
| `make_link_anyone_with_link` | 是否自動設為「任何擁有連結者皆可檢視」(預設 true) |

改完存檔,下次開啟工具就生效。

---

## 常見問題

**Q：每次上傳完都要重新授權 Google 嗎?**
不用。只有第一次。`token.json` 會記住你的登入。

**Q：可以多人使用嗎?**
可以,但每個人都要自己跑一次「取得 Google Drive API 金鑰」那段(用自己的 Google 帳號)。也可以共用同一個 `credentials.json`,但 `token.json` 要刪掉讓對方重新授權。

**Q：照片上傳後可以撤回嗎?**
程式只負責上傳,不會刪本機原檔。Google Drive 那邊用網頁版手動刪即可。

**Q：可以打包成 .exe 嗎?**
可以。裝 `pyinstaller` 後執行：
```bat
pip install pyinstaller
pyinstaller --onefile --windowed --name "LINE相片整理" main.py
```
產生的 `.exe` 放到桌面就能雙擊開啟(仍需要 `config.json`、`credentials.json`、`token.json` 在旁邊)。

**Q：群組名稱輸入錯了,怎麼刪除?**
打開 `config.json`,把不要的群組從 `groups` 陣列裡刪掉,存檔。

---

## 安全提醒

- `credentials.json` 和 `token.json` 都**不要上傳到 GitHub** 或分享給別人,它們等同你的 Google 帳號鑰匙。`.gitignore` 已經幫你擋掉這兩個檔案。
- 程式只會要求 `drive.file` 權限——意思是它**只看得到自己上傳的檔案**,看不到你雲端裡其他東西。
