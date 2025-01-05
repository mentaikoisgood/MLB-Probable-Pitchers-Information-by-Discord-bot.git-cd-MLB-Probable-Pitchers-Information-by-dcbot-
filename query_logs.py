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
        print("-" * 50)

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

print_logs(response['Items'])
