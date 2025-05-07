import streamlit as st
import pandas as pd
from datetime import datetime
import asyncio
from dotenv import load_dotenv
import os
from newsapi import NewsApiClient
import logging

# Suppress Streamlit warnings
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Load environment variables from .env file
load_dotenv()

# Streamlit page configuration
st.set_page_config(page_title="Indian News Feed", layout="wide")

# Minimalistic CSS for clean, mobile-friendly UI
st.markdown("""
    <style>
    body { font-family: 'Arial', sans-serif; background-color: #f5f5f5; }
    .news-card { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin: 10px; }
    .news-title { font-size: 1.2em; font-weight: bold; color: #333; }
    .news-source { font-size: 0.9em; color: #666; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 5px; padding: 10px 20px; }
    @media (max-width: 600px) { .news-card { padding: 10px; margin: 5px; } .news-title { font-size: 1em; } }
    </style>
""", unsafe_allow_html=True)

# Get secrets from .env
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=NEWSAPI_KEY) if NEWSAPI_KEY else None

# Function to fetch news from NewsAPI
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_indian_news(query="india"):
    if not newsapi:
        st.error("NewsAPI key is missing. Please check your .env file.")
        return []
    try:
        response = newsapi.get_everything(
            q=f"{query} india",
            language="en",
            sort_by="publishedAt"
        )
        if response["status"] != "ok":
            st.error(f"NewsAPI error: {response.get('message', 'Unknown error')}")
            return []
        articles = response.get("articles", [])
        st.write(f"Debug: Fetched {len(articles)} articles")  # Debugging output
        return articles[:10]  # Return top 10 news articles
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

# Main app
def main():
    st.title("Indian News Feed")
    st.markdown("Stay updated with live news from India, delivered with push notifications.")

    # Search bar for news topics
    search_query = st.text_input("Search News (e.g., politics, sports)", value="india")

    # Fetch and display news
    if search_query:
        with st.spinner("Fetching news..."):
            news_articles = fetch_indian_news(search_query)
        if news_articles:
            for article in news_articles:
                st.markdown(
                    f"""
                    <div class='news-card'>
                        <div class='news-title'><a href='{article['url']}' target='_blank'>{article['title']}</a></div>
                        <div class='news-source'>{article['source']['name']} | {article['publishedAt'][:10]}</div>
                        <p>{article.get('description', 'No description available.')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("No news articles found. Try a different search term or check your API key.")

    # Push notification subscription (client-side JS)
    if VAPID_PUBLIC_KEY and VAPID_PUBLIC_KEY != "placeholder_vapid_key":
        st.markdown(f"""
            <button id="subscribeButton">Enable Push Notifications</button>
            <script>
            async function subscribeToPush() {{
                if (!('serviceWorker' in navigator)) {{
                    alert('Service Worker not supported!');
                    return;
                }}
                try {{
                    const registration = await navigator.serviceWorker.register('/sw.js');
                    const subscription = await registration.pushManager.subscribe({{
                        userVisibleOnly: true,
                        applicationServerKey: '{VAPID_PUBLIC_KEY}'
                    }});
                    await fetch('/subscribe', {{
                        method: 'POST',
                        body: JSON.stringify(subscription),
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    alert('Subscribed to push notifications!');
                }} catch (error) {{
                    console.error('Subscription failed:', error);
                    alert('Failed to subscribe to push notifications.');
                }}
            }}
            document.getElementById('subscribeButton').onclick = subscribeToPush;
            </script>
        """, unsafe_allow_html=True)
    else:
        st.warning("VAPID public key is missing or invalid. Push notifications are disabled.")

# Run the app
if __name__ == "__main__":
    main()