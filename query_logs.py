import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('mlb_bot_logs')

def print_logs(items):
    for item in sorted(items, key=lambda x: x['timestamp'], reverse=True):
        print(f"\n時間: {item['timestamp']}")
        print(f"命令: {item['command']}")
        print(f"用戶: {item['user']}")
        print(f"伺服器: {item['guild']}")
        if 'content' in item:
            print(f"完整命令: {item['content']}")
        if 'channel' in item:
            print(f"頻道: {item['channel']}")
        print("-" * 50)

def print_stats(items):
    stats = {
        'total_commands': 0,
        'commands_by_type': {},
        'active_users': set(),
        'active_guilds': set()
    }
    
    for item in items:
        stats['total_commands'] += 1
        stats['commands_by_type'][item['command']] = stats['commands_by_type'].get(item['command'], 0) + 1
        stats['active_users'].add(item['user'])
        stats['active_guilds'].add(item['guild'])
    
    print("\n=== 統計資料 ===")
    print(f"總命令數: {stats['total_commands']}")
    print("\n命令使用次數:")
    for cmd, count in stats['commands_by_type'].items():
        print(f"- {cmd}: {count}")
    print(f"\n活躍用戶數: {len(stats['active_users'])}")
    print(f"使用的伺服器數: {len(stats['active_guilds'])}")

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
print_stats(response['Items'])
