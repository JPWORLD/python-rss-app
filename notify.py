import time
from dotenv import load_dotenv
import os
from newsapi import NewsApiClient
import requests

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

newsapi = NewsApiClient(api_key=NEWSAPI_KEY) if NEWSAPI_KEY else None

def fetch_latest_news():
    if not newsapi:
        return []
    try:
        response = newsapi.get_everything(q="india", sort_by="publishedAt")
        return response.get("articles", [])
    except:
        return []

def send_notification(title, body):
    requests.post(
        "http://localhost:5000/send_notification",
        json={"title": title, "body": body}
    )

last_article = None
while True:
    articles = fetch_latest_news()
    if articles and articles[0]["title"] != last_article:
        last_article = articles[0]["title"]
        send_notification("Breaking News", articles[0]["title"])
    time.sleep(300)