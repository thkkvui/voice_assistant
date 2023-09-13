import requests
import re
import math
from datetime import datetime
import json
import time
import pandas as pd
import boto3
import botocore.exceptions
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from urllib.parse import urlparse

# aws
aws_access_key_id = "Enter Your Access Key" # AWSアクセスキー
aws_secret_access_key = "Enter Your Secret Key" # AWSシークレットキー
region_name = "ap-northeast-1" # 任意のリージョンを選択
bucket_name = "Enter Your Bucket Name" # S3バケット

# goole calendar
calendar_id = "Enter Your Calendar Id" # カレンダーID
credential_file = "Enter Your File Path" # credentialのJSONファイル
scopes = ["https://www.googleapis.com/auth/calendar"] # 任意のスコープを選択

# alpha Vantage
AV_api_id = "Enter Your API Key" # Alpha VantageのAPIキー
news_vendors = ["www.reuters.com"] # 任意のベンダーを選択
currency_pairs = ["USD/JPY", "BTC/USD"] # 任意の通貨ペアを選択

# openweather
OP_api_id = "Enter Your API Key" # OpenWeatherのAPIキー
cityNames = {"札幌":"sapporo"} # 任意の都市を選択
cityLatitude = {"札幌":"43.0691"} # 都市の緯度を入力
cityLongitude = {"札幌":"141.3476"} # 都市の経度を入力
weatherConditions = {
    "clear sky":"晴れ",
    "few clouds":"晴れ",
    "scattered clouds":"くもり",
    "broken clouds":"くもり",
    "overcast clouds":"くもり",
    "light rain":"小雨",
    "rain":"雨",
    "moderate rain":"雨",
    "heavy intensity":"雨",
    "heavy intensity rain":"雨"
}

# time params
time_now = datetime.now()
year = time_now.year
month = time_now.month
day = time_now.day
hour = time_now.hour


def getWeather(city_value=None):
    
    target_date = datetime(year, month, day)
    diff_days = target_date - time_now
    diff_seconds = diff_days.total_seconds()
    day_counts = math.ceil(diff_seconds / 60 / 60 / 24)
    latitude = [v for k, v in cityLatitude.items() if k==city_value]
    longitude = [v for k, v in cityLongitude.items() if k==city_value]
    exclude = ["current,minutely,hourly,alerts"]

    weather_data = {"weather":""}
    try:
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={latitude[0]}&lon={longitude[0]}&exclude={exclude[0]}&appid={OP_api_id}&units=metric"
        res = requests.get(url)
        data = res.json()
        weather = data["daily"][day_counts]
        condition_JP = [v for k, v in weatherConditions.items() if k==weather["weather"][0]["description"]]
        temp_max = round(weather["temp"]["max"], 0)
        temp_min = round(weather["temp"]["min"], 0)
        pop = round(weather["pop"]*100, 0)
        weather_data["weather"] = [condition_JP[0], temp_max, temp_min, pop]
        print("weather data, done!")
    except Exception as e:
        print("Error: ", e)
    
    return weather_data


def getCurrencyMarket(currency_pairs=None):
    
    url = "https://www.alphavantage.co/query"
    currency_data = {"market":""}
    tmp = {}
    try:
        for i in currency_pairs:
            fc = i.split("/")[0]
            tc = i.split("/")[1]
            currency_params = {
                "function":"CURRENCY_EXCHANGE_RATE",
                "from_currency":fc,
                "to_currency":tc,
                "apikey":AV_api_id
            }
            res = requests.get(url, params=currency_params)
            data = res.json()["Realtime Currency Exchange Rate"]
            tmp.update({i:data["5. Exchange Rate"]})
            time.sleep(20) # get lag for API
        currency_data["market"] = tmp
        print("financial data, done!")
    except Exception as e:
        print("Error: ", e)
        
    return currency_data


def getNews():
    
    url = "https://www.alphavantage.co/query"
    news_data = {"news":""}
    tmp = {"news":""}
    try:
        news_params = {
            "function":"NEWS_SENTIMENT",
            "topics":"financial_markets",#financial_markets, #technology, #economy_macro
            "sort":"LATEST",
            "apikey":AV_api_id
        }
        res = requests.get(url, params=news_params)
        df = pd.DataFrame(res.json()["feed"])
        for i in range(len(df)):
            url = urlparse(df["url"][i]).netloc
            if url in news_vendors:
                tmp["news"] += ("\n" + df["title"][i])
        news_data["news"] = preprocess_news(tmp["news"])
        print("news data, done!")   
    except Exception as e:
        print("Error: ", e)

    return news_data


def getGoogleCalendar():
    
    credentials = service_account.Credentials.from_service_account_file(credential_file, scopes=scopes)
    service = build('calendar', 'v3', credentials=credentials)
    st = datetime(year, month, day, 0, 0, 0).isoformat() + 'Z'
    et = datetime(year, month, day, 23, 59, 59).isoformat() + 'Z'

    calendar_data = {"calendar":""}
    tmp = []
    try:
        results = service.events().list(calendarId=calendar_id, timeMin=st, timeMax=et, singleEvents=True).execute()
        events = results.get('items', [])
        if not events:
            tmp.append({"event":"予定がありません", "start":None, "end":None})
        else:
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                summary = event.get("summary", "No Summary")
                tmp.append({"event":summary, "start":start, "end":end})
        calendar_data["calendar"] = tmp
        print("calendar data, done!") 
    except HttpError as e:
        print('An error occurred: %s' % e)

    return calendar_data


def preprocess_news(text):
    lines = text.split('\n')
    re_text = [re.sub(r'[:|]+', ' ', re.sub(r'\s+', ' ', line)).strip() for line in lines if line.strip()]
    return re_text


def s3Upload(data):
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    s3 = session.client("s3")
    
    try:
        s3.put_object(Bucket=bucket_name, Key=data["name"], Body=json.dumps(data["content"]))
        print(f"Uploaded {data['name']} to {bucket_name}")
    except botocore.exceptions.ClientError as e:
        print(f"Error while uploading to S3 {data['name']}: {e}")
    
    
def main():
    data_contents = getWeather("札幌")
    data_contents.update(getCurrencyMarket(currency_pairs))
    data_contents.update(getNews())
    data_contents.update(getGoogleCalendar())

    upload_data = {"name":datetime(year, month, day, hour).strftime("%Y-%m-%d-%H"), "content": data_contents}
    s3Upload(upload_data)
    

if __name__ == "__main__":
    main()