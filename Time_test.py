import discord
import time
import datetime
from discord.ext import tasks, commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print('目前登入身份：', client.user)
    game = discord.Game(name="笑死")
    await client.change_presence(status=discord.Status.online, activity=game)
    await client.add_cog(TaskTime(client))

class TaskTime(commands.Cog):
    # 臺灣時區 UTC+8
    tz = datetime.timezone(datetime.timedelta(hours = 8))
    # 設定每日十二點執行一次函式
    everyday_time = datetime.time(hour = 14, minute = 25, tzinfo = tz)

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.everyday.start()

    # 每日十二點發送 "晚安!瑪卡巴卡!" 訊息
    @tasks.loop(time = everyday_time)
    async def everyday(self):
        # 設定發送訊息的頻道ID
        channel_id = 1232217167311798296
        channel = self.bot.get_channel(channel_id)
        embed = discord.Embed(
            title = "🛏 晚安！瑪卡巴卡！",
            description = f"🕛 現在時間 {datetime.date.today()} 00:00",
            color = discord.Color.orange()
        )
        await channel.send(embed = embed)

file = open("token.txt","r")
token = file.read()
client.run(token)