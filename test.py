from newsapi import NewsApiClient
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("NEWSAPI_KEY")

if not api_key:
    print("Error: NEWSAPI_KEY is missing from .env")
    exit(1)

newsapi = NewsApiClient(api_key=api_key)

try:
    articles = newsapi.get_everything(q="india", sort_by="publishedAt")
    print(articles)
except Exception as e:
    print(f"Error: {e}")