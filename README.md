# MLB Discord Bot

這是一個用於查詢 MLB（美國職棒大聯盟）資訊的 Discord 機器人。

## 功能

- **查詢投手資訊**
- **查看今日比賽賽程**
- **顯示所有 MLB 球隊列表**
- **查詢指定日期的比賽歷史**
- **查看球隊最近的比賽記錄**
- **查詢球員當年度統計資料**

## 指令列表

所有指令都使用 `!` 作為前綴：

- `!pitcher NYY` - 查詢洋基隊投手資訊
- `!pitcher LAD` - 查詢道奇隊投手資訊
- `!schedule` - 顯示今日所有比賽
- `!teams` - 顯示所有 MLB 球隊代號
- `!history NYY 2023-10-01` - 查詢洋基隊在指定日期的比賽
- `!recent NYY 5` - 查詢洋基隊最近 5 場比賽記錄
- `!hstat Freddie Freeman` - 查詢Freddie Freeman今年數據
- `!pstat Yoshinobu Yamamoto` - 查詢Yoshinobu Yamamoto今年數據
- `!quote` - 隨機抽取一句棒球名言

## 安裝步驟

1. **克隆專案**：
    ```bash
    git clone https://github.com/mentaikoisgood/MLB-Probable-Pitchers-Information-by-Discord-bot.git
    ```

2. **安裝依賴**：
    ```bash
    pip install -r requirements.txt
    ```

3. **設置配置文件**：
    - 複製 `config.json.example` 為 `config.json`
    - 在 `config.json` 中填入您的 Discord Bot Token

4. **運行機器人**：
    ```bash
    python Discord.py
    ```

## 注意事項

- 球隊可使用簡寫（如 `NYY`, `LAD`, `BOS`）
- 日期格式為 `YYYY-MM-DD`
- `recent` 命令預設顯示最近 3 場比賽
