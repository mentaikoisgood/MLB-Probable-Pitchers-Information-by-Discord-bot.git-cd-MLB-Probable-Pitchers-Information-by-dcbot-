import discord
from discord.ext import commands
import Crawling
import json

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


@bot.command(help='獲取MLB投手資訊\n例：!pitcher NYY')
async def pitcher(ctx, team=None):
    """獲取MLB投手資訊"""
    if team is None:
        await ctx.send("請提供球隊代號！例如：!pitcher NYY")
        return

    try:
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

# 在這裡替換為您的機器人 Token
bot.run(config['token'])
