import boto3
from datetime import datetime, timedelta
from collections import Counter
from tabulate import tabulate
import pytz  # 需要安裝: pip3 install pytz

# 設置台灣時區
tw_tz = pytz.timezone('Asia/Taipei')

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('mlb_bot_logs')

def convert_to_tw_time(timestamp_str):
    # 將字符串轉換為 datetime 對象
    dt = datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
    # 設置為 UTC 時間
    dt = pytz.utc.localize(dt)
    # 轉換為台灣時間
    tw_time = dt.astimezone(tw_tz)
    return tw_time.strftime('%Y-%m-%d %H:%M:%S')

def print_logs(items):
    for item in sorted(items, key=lambda x: x['timestamp'], reverse=True):
        print(f"\n時間: {convert_to_tw_time(item['timestamp'])} (台灣時間)")
        print(f"命令: {item['command']}")
        print(f"用戶: {item['user']}")
        print(f"伺服器: {item['guild']}")
        print(f"頻道: {item.get('channel', 'N/A')}")
        print(f"完整命令: {item.get('content', 'N/A')}")
        print("-" * 50)

def get_team_from_command(content):
    """從命令內容中提取球隊名稱"""
    if not content:
        return None
    parts = content.split()
    if len(parts) > 1 and parts[0] in ['!pitcher', '!schedule']:
        return parts[1].upper()
    return None

def print_detailed_stats(items):
    stats = {
        'total_commands': 0,
        'commands_by_type': Counter(),
        'users_by_command': {},
        'guilds_by_command': {},
        'hourly_usage': Counter(),
        'channel_usage': Counter(),
        'active_users': Counter(),
        'active_guilds': Counter(),
        'team_queries': Counter()  # 新增：球隊查詢統計
    }
    
    for item in items:
        # 轉換為台灣時間
        tw_time = datetime.strptime(convert_to_tw_time(item['timestamp']), '%Y-%m-%d %H:%M:%S')
        
        # 基本計數
        stats['total_commands'] += 1
        command = item['command']
        user = item['user']
        guild = item['guild']
        channel = item.get('channel', 'unknown')
        
        # 命令使用統計
        stats['commands_by_type'][command] += 1
        
        # 用戶活躍度
        stats['active_users'][user] += 1
        
        # 伺服器活躍度
        stats['active_guilds'][guild] += 1
        
        # 頻道使用統計
        stats['channel_usage'][channel] += 1
        
        # 每小時使用統計 (使用台灣時間)
        stats['hourly_usage'][tw_time.hour] += 1
        
        # 用戶命令偏好
        if command not in stats['users_by_command']:
            stats['users_by_command'][command] = Counter()
        stats['users_by_command'][command][user] += 1
        
        # 伺服器命令偏好
        if command not in stats['guilds_by_command']:
            stats['guilds_by_command'][command] = Counter()
        stats['guilds_by_command'][command][guild] += 1
        
        # 添加球隊統計
        content = item.get('content')
        team = get_team_from_command(content)
        if team:
            stats['team_queries'][team] += 1

    # 輸出統計結果
    print("\n=== 詳細統計資料 ===")
    print(f"\n總命令使用次數: {stats['total_commands']}")
    
    print("\n命令使用排行:")
    command_table = [[cmd, count] for cmd, count in stats['commands_by_type'].most_common()]
    print(tabulate(command_table, headers=['命令', '次數'], tablefmt='grid'))
    
    print("\n最活躍用戶:")
    user_table = [[user, count] for user, count in stats['active_users'].most_common(5)]
    print(tabulate(user_table, headers=['用戶', '命令次數'], tablefmt='grid'))
    
    print("\n最活躍伺服器:")
    guild_table = [[guild, count] for guild, count in stats['active_guilds'].most_common(5)]
    print(tabulate(guild_table, headers=['伺服器', '命令次數'], tablefmt='grid'))
    
    print("\n頻道使用統計:")
    channel_table = [[channel, count] for channel, count in stats['channel_usage'].most_common()]
    print(tabulate(channel_table, headers=['頻道', '次數'], tablefmt='grid'))
    
    print("\n每小時使用統計 (台灣時間):")
    hours = range(24)
    hour_table = [[f"{hour:02d}:00", stats['hourly_usage'][hour]] for hour in hours]
    print(tabulate(hour_table, headers=['時段', '次數'], tablefmt='grid'))
    
    # 添加球隊統計輸出
    if stats['team_queries']:
        print("\n最常查詢的球隊:")
        team_table = [[team, count] for team, count in stats['team_queries'].most_common()]
        print(tabulate(team_table, headers=['球隊', '查詢次數'], tablefmt='grid'))
        
        # 計算每個用戶最常查詢的球隊
        user_team_prefs = {}
        for item in items:
            user = item['user']
            team = get_team_from_command(item.get('content'))
            if team:
                if user not in user_team_prefs:
                    user_team_prefs[user] = Counter()
                user_team_prefs[user][team] += 1
        
        print("\n用戶最愛查詢的球隊:")
        user_team_table = []
        for user, team_counts in user_team_prefs.items():
            if team_counts:
                favorite_team, count = team_counts.most_common(1)[0]
                user_team_table.append([user, favorite_team, count])
        print(tabulate(user_team_table, headers=['用戶', '最愛球隊', '查詢次數'], tablefmt='grid'))

    return stats

def save_stats_to_file(stats, items):
    """將統計結果保存到文件"""
    current_time = datetime.now(tw_tz).strftime('%Y%m%d_%H%M%S')
    filename = f'bot_stats_{current_time}.txt'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=== MLB Bot 使用統計報告 ===\n")
        f.write(f"生成時間: {datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M:%S')} (台灣時間)\n\n")
        
        # 基本統計
        f.write(f"總命令使用次數: {stats['total_commands']}\n\n")
        
        # 命令使用排行
        f.write("命令使用排行:\n")
        command_table = [[cmd, count] for cmd, count in stats['commands_by_type'].most_common()]
        f.write(tabulate(command_table, headers=['命令', '次數'], tablefmt='grid'))
        f.write("\n\n")
        
        # 最活躍用戶
        f.write("最活躍用戶:\n")
        user_table = [[user, count] for user, count in stats['active_users'].most_common(5)]
        f.write(tabulate(user_table, headers=['用戶', '命令次數'], tablefmt='grid'))
        f.write("\n\n")
        
        # 頻道使用統計
        f.write("頻道使用統計:\n")
        channel_table = [[channel, count] for channel, count in stats['channel_usage'].most_common()]
        f.write(tabulate(channel_table, headers=['頻道', '次數'], tablefmt='grid'))
        f.write("\n\n")
        
        # 每小時使用統計
        f.write("每小時使用統計 (台灣時間):\n")
        hours = range(24)
        hour_table = [[f"{hour:02d}:00", stats['hourly_usage'][hour]] for hour in hours]
        f.write(tabulate(hour_table, headers=['時段', '次數'], tablefmt='grid'))
        f.write("\n\n")
        
        # 球隊統計
        if stats['team_queries']:
            f.write("最常查詢的球隊:\n")
            team_table = [[team, count] for team, count in stats['team_queries'].most_common()]
            f.write(tabulate(team_table, headers=['球隊', '查詢次數'], tablefmt='grid'))
            f.write("\n\n")
            
            # 用戶最愛球隊
            user_team_prefs = {}
            for item in items:
                user = item['user']
                team = get_team_from_command(item.get('content'))
                if team:
                    if user not in user_team_prefs:
                        user_team_prefs[user] = Counter()
                    user_team_prefs[user][team] += 1
            
            f.write("用戶最愛查詢的球隊:\n")
            user_team_table = []
            for user, team_counts in user_team_prefs.items():
                if team_counts:
                    favorite_team, count = team_counts.most_common(1)[0]
                    user_team_table.append([user, favorite_team, count])
            f.write(tabulate(user_team_table, headers=['用戶', '最愛球隊', '查詢次數'], tablefmt='grid'))
            f.write("\n\n")
        
        # 最近的命令記錄
        f.write("=== 最近的命令記錄 ===\n")
        for item in sorted(items, key=lambda x: x['timestamp'], reverse=True):
            f.write(f"\n時間: {convert_to_tw_time(item['timestamp'])} (台灣時間)\n")
            f.write(f"命令: {item['command']}\n")
            f.write(f"用戶: {item['user']}\n")
            f.write(f"伺服器: {item['guild']}\n")
            f.write(f"頻道: {item.get('channel', 'N/A')}\n")
            f.write(f"完整命令: {item.get('content', 'N/A')}\n")
            f.write("-" * 50 + "\n")
    
    print(f"\n統計報告已保存到文件: {filename}")

# 獲取最近24小時的日誌
now = datetime.now(tw_tz)
response = table.scan(
    FilterExpression='#ts >= :start_time',
    ExpressionAttributeNames={
        '#ts': 'timestamp'
    },
    ExpressionAttributeValues={
        ':start_time': str(now - timedelta(hours=24))
    }
)

print("=== 最近的命令記錄 ===")
print_logs(response['Items'])
stats = print_detailed_stats(response['Items'])
save_stats_to_file(stats, response['Items'])
