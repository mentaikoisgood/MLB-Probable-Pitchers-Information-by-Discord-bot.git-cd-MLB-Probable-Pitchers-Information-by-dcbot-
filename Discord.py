import discord
from discord.ext import commands
import Crawling
import json
import boto3
from datetime import datetime
import requests

# 讀取配置文件
with open('config.json') as f:
    config = json.load(f)

# 明確設置所需的 intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# 自定義幫助命令


class CustomHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__(
            no_category='指令列表',
            commands_heading="可用指令："
        )

    async def send_bot_help(self, mapping):
        # 添加自定義幫助信息
        help_text = """
**MLB資訊查詢機器人使用說明**
所有指令都使用 ! 作為前綴

**指令範例：**
`!pitcher NYY` - 查詢洋基隊投手資訊
`!pitcher LAD` - 查詢道奇隊投手資訊
`!schedule` - 顯示今日所有比賽
`!teams` - 顯示所有MLB球隊代號
`!history NYY 2023-10-01` - 查詢洋基隊在指定日期的比賽
`!recent NYY 5` - 查詢洋基隊最近5場比賽記錄

**提示：**
- 球隊可使用簡寫（如 NYY, LAD, BOS）
- 日期格式為 YYYY-MM-DD
- recent 命令預設顯示最近3場比賽
"""
        await self.get_destination().send(help_text)


# 使用自定義幫助命令
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=CustomHelpCommand()
)


@bot.event
async def on_ready():
    print(f'機器人已登入為 {bot.user.name}')
    print('------')


# 初始化 DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
command_logs = dynamodb.Table('mlb_bot_logs')


@bot.command(help='獲取MLB投手資訊\n例：!pitcher NYY')
async def pitcher(ctx, team=None):
    """獲取MLB投手資訊"""
    if team is None:
        await ctx.send("請提供球隊代號！例如：!pitcher NYY")
        return

    try:
        # 記錄命令使用
        command_logs.put_item(
            Item={
                'command_id': str(datetime.now().timestamp()),
                'command': 'pitcher',
                'user': str(ctx.author),
                'guild': str(ctx.guild),
                'params': team,
                'timestamp': str(datetime.now())
            }
        )
        pitcher_info = Crawling.get_pitcher_info(team)
        await ctx.send(pitcher_info)
    except Exception as e:
        await ctx.send(f"獲取投手資訊時出錯：{str(e)}")


@bot.command(help='獲取今日比賽賽程\n例：!schedule')
async def schedule(ctx):
    """獲取今日比賽賽程"""
    try:
        schedule_info = Crawling.get_schedule()
        await ctx.send(schedule_info)
    except Exception as e:
        await ctx.send(f"獲取賽程資訊時出錯：{str(e)}")


@bot.command(help='顯示所有MLB球隊列表\n例：!teams')
async def teams(ctx):
    """顯示所有MLB球隊列表"""
    try:
        teams_info = Crawling.get_all_teams()
        await ctx.send(teams_info)
    except Exception as e:
        await ctx.send(f"獲取球隊列表時出錯：{str(e)}")


@bot.command(help='查詢指定日期的比賽歷史\n例：!history NYY 2023-10-01')
async def history(ctx, team, date=None):
    """查詢指定日期的比賽歷史"""
    try:
        history_info = Crawling.get_game_history(team, date)
        await ctx.send(history_info)
    except Exception as e:
        await ctx.send(f"獲取歷史資料時出錯：{str(e)}")


@bot.command(help='查詢球隊最近的比賽數據\n例：!recent NYY 5\n數字表示要查詢的最近幾場比賽（預設為3場）')
async def recent(ctx, team, games=3):
    """查詢球隊最近的比賽數據"""
    try:
        recent_info = Crawling.get_recent_games(team, games)
        await ctx.send(recent_info)
    except Exception as e:
        await ctx.send(f"獲取最近比賽資料時出錯：{str(e)}")


@bot.event
async def on_command(ctx):
    try:
        # 更詳細的日誌記錄
        command_logs.put_item(
            Item={
                'command_id': str(datetime.now().timestamp()),
                'command': ctx.command.name,
                'user': str(ctx.author),
                'user_id': str(ctx.author.id),
                'guild': str(ctx.guild),
                'guild_id': str(ctx.guild.id),
                'channel': str(ctx.channel),
                'channel_id': str(ctx.channel.id),
                'content': ctx.message.content,
                'timestamp': str(datetime.now())
            }
        )
        print(f"命令已記錄: {ctx.command.name} by {ctx.author} in {ctx.guild}")
    except Exception as e:
        print(f"日誌記錄錯誤: {str(e)}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # 獲取用戶輸入的錯誤命令
        wrong_command = ctx.message.content.split()[0][1:]  # 移除前綴 '!'
        await ctx.send(f"❌ 命令 `{wrong_command}` 不存在\n請使用 `!help` 查看所有可用命令")
    else:
        # 處理其他類型的錯誤
        await ctx.send(f"❌ 發生錯誤：{str(error)}")

    try:
        command_logs.put_item(
            Item={
                'command_id': f"error_{str(datetime.now().timestamp())}",
                'type': 'error',
                'command': ctx.command.name if ctx.command else 'unknown',
                'user': str(ctx.author),
                'guild': str(ctx.guild),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'timestamp': str(datetime.now())
            }
        )
    except Exception as e:
        print(f"錯誤日誌記錄失敗: {str(e)}")


def get_command_stats():
    response = command_logs.scan()
    stats = {
        'total_commands': 0,
        'commands_by_type': {},
        'active_users': set(),
        'active_guilds': set()
    }
    
    for item in response['Items']:
        stats['total_commands'] += 1
        stats['commands_by_type'][item['command']] = stats['commands_by_type'].get(item['command'], 0) + 1
        stats['active_users'].add(item['user'])
        stats['active_guilds'].add(item['guild'])
    
    return stats


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith('!'):
        try:
            # 記錄所有以 ! 開頭的消息
            command_logs.put_item(
                Item={
                    'command_id': str(datetime.now().timestamp()),
                    'command': message.content.split()[0][1:],  # 移除 ! 並獲取命令名
                    'user': str(message.author),
                    'user_id': str(message.author.id),
                    'guild': str(message.guild),
                    'guild_id': str(message.guild.id),
                    'channel': str(message.channel),
                    'channel_id': str(message.channel.id),
                    'content': message.content,
                    'timestamp': str(datetime.now())
                }
            )
            print(f"消息已記錄: {message.content} by {message.author} in {message.guild}")
        except Exception as e:
            print(f"日誌記錄錯誤: {str(e)}")
    
    await bot.process_commands(message)

#get quote function
@bot.command(help="隨機獲取一條棒球名言")
async def quote(ctx):
    """使用 API Gateway 觸發 Lambda 並獲取棒球名言"""
    try:
        # ✅ 使用剛剛找到的 API Gateway URL
        api_url = "https://mh0bkfnge4.execute-api.ap-northeast-1.amazonaws.com/"

        # ✅ 發送 GET 請求到 API Gateway
        response = requests.get(api_url)
        
        # ✅ 如果回應成功，解析回傳的 JSON
        if response.status_code == 200:
            data = response.json()
            # 確保正確解析 Lambda 回傳的資料格式
            quote = data.get('body', {}).get('quote', "❌ 無法解析名言")
            await ctx.send(f"🎯 **棒球名言** 🎯\n{quote}")
        else:
            await ctx.send(f"❌ API 呼叫失敗，狀態碼: {response.status_code}")

    except Exception as e:
        await ctx.send(f"❌ 發生錯誤：{str(e)}")

try:
    bot.run(config['token'])
except discord.errors.LoginFailure:
    print("錯誤：Discord Bot Token 無效")
except Exception as e:
    print(f"錯誤：Bot 無法啟動")
    print(f"錯誤詳情：{str(e)}")
    print("請檢查：")
    print("1. 網路連接是否正常")
    print("2. Discord Bot Token 是否正確")
    print("3. Discord API 服務是否正常")
