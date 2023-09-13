import boto3
import botocore.exceptions
from datetime import datetime
import random
import json

# aws
aws_access_key_id = "Enter Your Access Key"
aws_secret_access_key = "Enter Your Secret Key"
region_name = "ap-northeast-1" # 任意のリージョンを選択
bucket_name = "Enter Your Bucket Name"

# time params
time_now = datetime.now()
year = time_now.year
month = time_now.month
day = time_now.day
hour = time_now.hour


def s3GetData():
    
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    s3 = session.client("s3")

    try:
        res = s3.get_object(Bucket=bucket_name, Key=datetime(year, month, day, hour).strftime("%Y-%m-%d-%H"))

        data = res['Body'].read().decode('unicode-escape')
        data = json.loads(data)

    except botocore.exceptions.ClientError as e:
        print(f"Error loading data from S3: {e}")
        
    return data


def getContext(data):
    
    weather = f"今日の天気は{data['weather'][0]}, 予想最高気温は{round(data['weather'][1], 0)}度, 予想最低気温は{round(data['weather'][2],0)}度, 降水確率は{round(data['weather'][3],0)}%です。"
    
    market = f"ドル円は{data['market']['USD/JPY']}, ビットコインは{data['market']['BTC/USD']}です。"
    
    n = random.sample(list(range(len(data['news']))), 1)
    news = f"最新のニュースは{data['news'][n[0]]}です。"
    
    events = data["calendar"]
    event = ""
    if events[0]["event"] == "予定がありません":
        calendar = "今日は予定がありません"
    else:
        for e in events:
            start = datetime.fromisoformat(e["start"])
            end = datetime.fromisoformat(e["end"])
            event += f"{start.hour}:{start.minute}から{end.hour}:{end.minute}まで{e['event']}"
        calendar = f"今日は{event}が予定されています。"
    context = weather + market + news + calendar
    
    return context


def main():
    data = s3GetData()
    context = getContext(data)

    return context
    
    
if __name__ == "__main__":
    main()