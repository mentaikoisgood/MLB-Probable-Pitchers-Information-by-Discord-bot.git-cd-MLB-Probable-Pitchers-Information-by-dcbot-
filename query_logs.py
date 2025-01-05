import boto3
from datetime import datetime, timedelta
from collections import Counter
from tabulate import tabulate  # 需要先安裝: pip install tabulate

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('mlb_bot_logs')

def print_logs(items):
    for item in sorted(items, key=lambda x: x['timestamp'], reverse=True):
        print(f"\n時間: {item['timestamp']}")
        print(f"命令: {item['command']}")
        print(f"用戶: {item['user']}")
        print(f"伺服器: {item['guild']}")
        print(f"頻道: {item.get('channel', 'N/A')}")
        print(f"完整命令: {item.get('content', 'N/A')}")
        print("-" * 50)

def print_detailed_stats(items):
    stats = {
        'total_commands': 0,
        'commands_by_type': Counter(),
        'users_by_command': {},
        'guilds_by_command': {},
        'hourly_usage': Counter(),
        'channel_usage': Counter(),
        'active_users': Counter(),
        'active_guilds': Counter()
    }
    
    for item in items:
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
        
        # 每小時使用統計
        hour = datetime.strptime(item['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S').hour
        stats['hourly_usage'][hour] += 1
        
        # 用戶命令偏好
        if command not in stats['users_by_command']:
            stats['users_by_command'][command] = Counter()
        stats['users_by_command'][command][user] += 1
        
        # 伺服器命令偏好
        if command not in stats['guilds_by_command']:
            stats['guilds_by_command'][command] = Counter()
        stats['guilds_by_command'][command][guild] += 1

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
    
    print("\n每小時使用統計:")
    hours = range(24)
    hour_table = [[f"{hour:02d}:00", stats['hourly_usage'][hour]] for hour in hours]
    print(tabulate(hour_table, headers=['時段', '次數'], tablefmt='grid'))

# 獲取最近24小時的日誌
response = table.scan(
    FilterExpression='#ts >= :start_time',
    ExpressionAttributeNames={
        '#ts': 'timestamp'
    },
    ExpressionAttributeValues={
        ':start_time': str(datetime.now() - timedelta(hours=24))
    }
)

print("=== 最近的命令記錄 ===")
print_logs(response['Items'])
print_detailed_stats(response['Items'])
