# MLB Probable Pitchers Information Discord Bot

這是一個 Discord bot，可以查詢 MLB 的投手資訊和賽程。

## 功能

- `!help` - 顯示所有可用命令
- `!teams` - 顯示所有球隊代號
- `!pitcher [team]` - 查詢指定球隊的投手資訊
- `!schedule [team]` - 查詢指定球隊的賽程

## 新增功能

- DynamoDB 數據記錄
- 使用統計分析
  - 命令使用次數統計
  - 用戶活躍度分析
  - 球隊查詢統計
  - 每小時使用統計
- 統計報告生成（自動保存為文件）

## 安裝需求

1. Python 3.8 或更高版本
2. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```

## 環境設置

1. Discord Bot Token
2. AWS 憑證（用於 DynamoDB）
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_DEFAULT_REGION

## 使用方法

1. 克隆倉庫
2. 安裝依賴
3. 設置環境變量
4. 運行 bot：
   ```bash
   python Discord.py
   ```

## 統計分析

使用 `query_logs.py` 查看使用統計：
```bash
python query_logs.py
```

統計報告會自動保存為文件，包含：
- 命令使用排行
- 最活躍用戶
- 最常查詢的球隊
- 每小時使用統計
- 詳細的命令記錄
