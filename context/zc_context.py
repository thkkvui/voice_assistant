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
        res = s3.get_object(Bucket=bucket_name, Key=datetime(year, month, day, hour).strftime("%Y-%m-%d-%H"))# S3オブジェクト名に合わせてyear, month, day, hourを入力

        data = res['Body'].read().decode('unicode-escape')
        data = json.loads(data)

    except botocore.exceptions.ClientError as e:
        print(f"Error loading data from S3: {e}")
        
    return data


def getContext(data):
    
    context = {"天気":f"今日の天気は{data['weather'][0]}, 予想最高気温は{round(data['weather'][1], 0)}℃, 予想最低気温は{round(data['weather'][2],0)}℃, 降水確率は{round(data['weather'][3],0)}%です。"}
    context.update({"マーケット":f"現在のドル円は{data['market']['USD/JPY']}、 ユーロドルは{data['market']['EUR/USD']}、ポンドドルは{data['market']['GBP/USD']}です。"})
    
    n = random.sample(list(range(len(data['news']))), 3)
    context.update({"ニュース":f"Here is the latest news. {data['news'][n[0]]}. {data['news'][n[1]]}. {data['news'][n[2]]}."})
    
    events = data["calendar"]
    event = ""
    if events[0]["event"] == "予定がありません":
        context.update({"予定":"今日は予定がありません"})
    else:
        for e in events:
            start = datetime.fromisoformat(e["start"])
            end = datetime.fromisoformat(e["end"])
            event += f"{start.hour}時{start.minute}分から{end.hour}時{end.minute}分まで{e['event']}、"
        context.update({"予定":f"今日は{event}が予定されています。"})
    
    return context


def main():
    data = s3GetData()
    context = getContext(data)
    
    
if __name__ == "__main__":
    main()