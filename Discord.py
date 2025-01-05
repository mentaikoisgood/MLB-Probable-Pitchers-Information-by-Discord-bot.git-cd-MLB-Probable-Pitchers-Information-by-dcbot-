import discord
from discord.ext import commands
import json
import boto3
from datetime import datetime
import requests

# ✅ 讀取配置檔案
with open('config.json') as f:
    config = json.load(f)

# ✅ 正確的 API Gateway URL
API_URL = "https://9fy9znkf2m.execute-api.ap-northeast-1.amazonaws.com"

# ✅ 設定 Discord Bot Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# ✅ 自定義幫助命令
class CustomHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__(
            no_category='指令列表',
            commands_heading="可用指令："
        )

    async def send_bot_help(self, mapping):
        help_text = """
**MLB資訊查詢機器人使用說明**
所有指令都使用 ! 作為前綴

**指令範例：**
`!pitcher NYY` - 查詢洋基隊投手資訊
`!schedule` - 顯示今日所有比賽
`!teams` - 顯示所有MLB球隊代號
`!history NYY 2023-10-01` - 查詢洋基隊在指定日期的比賽
`!recent NYY 5` - 查詢洋基隊最近5場比賽記錄
`!quote` - 獲取隨機棒球名言
"""
        await self.get_destination().send(help_text)

# ✅ 初始化 Bot
bot = commands.Bot(command_prefix='!', intents=intents, help_command=CustomHelpCommand())

# ✅ 初始化 DynamoDB 連線
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
command_logs = dynamodb.Table('mlb_bot_logs')

# ✅ 新增 `!quote` 指令 (正確使用 API Gateway)
@bot.command(help="隨機獲取一條棒球名言")
async def quote(ctx):
    try:
        # ✅ 使用正確的 API Gateway URL
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()

        # ✅ 直接回傳純文字
        quote = response.text
        await ctx.send(f"🎯 **棒球名言** 🎯\n{quote}")

    except requests.exceptions.RequestException as e:
        await ctx.send(f"❌ 網路錯誤：{e}")
    except Exception as e:
        await ctx.send(f"❌ 發生未預期的錯誤：{str(e)}")

# ✅ 新增 `!quote_test` 指令 (測試 API 是否正常)
@bot.command(help="測試 API Gateway 是否正常")
async def quote_test(ctx):
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        await ctx.send(f"✅ API 測試正常，原始回應：\n```{response.text}```")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"❌ 無法連線到 API Gateway: {e}")

# ✅ 原有指令保留
@bot.command(help='獲取MLB投手資訊\n例：!pitcher NYY')
async def pitcher(ctx, team=None):
    if team is None:
        await ctx.send("請提供球隊代號！例如：!pitcher NYY")
        return
    try:
        pitcher_info = Crawling.get_pitcher_info(team)
        await ctx.send(pitcher_info)
    except Exception as e:
        await ctx.send(f"❌ 獲取投手資訊時出錯：{str(e)}")


@bot.command(help='獲取今日比賽賽程\n例：!schedule')
async def schedule(ctx):
    try:
        schedule_info = Crawling.get_schedule()
        await ctx.send(schedule_info)
    except Exception as e:
        await ctx.send(f"❌ 獲取賽程資訊時出錯：{str(e)}")


@bot.command(help='顯示所有MLB球隊列表\n例：!teams')
async def teams(ctx):
    try:
        teams_info = Crawling.get_all_teams()
        await ctx.send(teams_info)
    except Exception as e:
        await ctx.send(f"❌ 獲取球隊列表時出錯：{str(e)}")

# ✅ 機器人上線事件
@bot.event
async def on_ready():
    print(f'✅ 機器人已登入為 {bot.user.name}')

# ✅ 日誌記錄
@bot.event
async def on_command(ctx):
    try:
        command_logs.put_item(
            Item={
                'command_id': str(datetime.now().timestamp()),
                'command': ctx.command.name,
                'user': str(ctx.author),
                'guild': str(ctx.guild),
                'timestamp': str(datetime.now())
            }
        )
        print(f"✅ 命令已記錄: {ctx.command.name} by {ctx.author}")
    except Exception as e:
        print(f"❌ 日誌記錄錯誤: {str(e)}")

# ✅ 錯誤處理
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ 命令不存在，請使用 `!help` 查看可用指令")
    else:
        await ctx.send(f"❌ 發生錯誤：{str(error)}")

# ✅ 啟動 Discord Bot
try:
    bot.run(config['token'])
except discord.errors.LoginFailure:
    print("❌ 錯誤：Token 無效")
except Exception as e:
    print(f"❌ Bot 無法啟動：{str(e)}")
