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

# Enhanced CSS for beautiful, tile-based UI
st.markdown("""
    <style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f6; }
    .header { text-align: center; padding: 20px; background-color: #007bff; color: white; border-radius: 10px; margin-bottom: 20px; }
    .header h1 { font-size: 2.5em; margin: 0; }
    .header p { font-size: 1.2em; margin: 5px 0; }
    .search-bar { margin: 20px 0; text-align: center; }
    .search-bar input { padding: 10px; width: 50%; border-radius: 5px; border: 1px solid #ccc; font-size: 1em; }
    .tile-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; padding: 20px; }
    .news-tile { background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); overflow: hidden; transition: transform 0.2s; }
    .news-tile:hover { transform: translateY(-5px); }
    .news-image { width: 100%; height: 150px; object-fit: cover; }
    .news-content { padding: 15px; }
    .news-title { font-size: 1.3em; font-weight: bold; color: #333; margin: 0 0 10px; }
    .news-source { font-size: 0.9em; color: #666; margin-bottom: 10px; }
    .news-summary { font-size: 1em; color: #444; line-height: 1.5; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 5px; padding: 10px 20px; margin: 10px; }
    @media (max-width: 600px) {
        .tile-grid { grid-template-columns: 1fr; }
        .news-tile { margin: 0 10px; }
        .search-bar input { width: 80%; }
        .header h1 { font-size: 2em; }
    }
    </style>
""", unsafe_allow_html=True)

# Get secrets from .env
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=NEWSAPI_KEY) if NEWSAPI_KEY else None

# Initialize session state
if 'news_articles' not in st.session_state:
    st.session_state.news_articles = []
if 'last_query' not in st.session_state:
    st.session_state.last_query = "india"

# Function to generate a summary
def generate_summary(description):
    if not description or description == "No description available.":
        return "Summary not available."
    sentences = description.split(". ")
    summary = sentences[0] + "." if len(sentences) > 0 else description
    return summary[:150] + "..." if len(summary) > 150 else summary

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
        return articles[:10]  # Return top 10 news articles
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

# Main app
def main():
    # Header
    st.markdown("""
        <div class="header">
            <h1>Indian News Feed</h1>
            <p>Stay updated with the latest news from India, beautifully presented.</p>
        </div>
    """, unsafe_allow_html=True)

    # Search bar and refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search News (e.g., politics, sports)", value="india", key="search", help="Enter a topic to filter news")
    with col2:
        if st.button("Refresh"):
            st.session_state.news_articles = []
            st.session_state.last_query = search_query

    # Fetch news only if query changes or refresh is clicked
    if search_query != st.session_state.last_query or not st.session_state.news_articles:
        with st.spinner("Fetching news..."):
            st.session_state.news_articles = fetch_indian_news(search_query)
            st.session_state.last_query = search_query

    # Display news
    if st.session_state.news_articles:
        st.write(f"Debug: Displaying {len(st.session_state.news_articles)} articles")
        st.markdown('<div class="tile-grid">', unsafe_allow_html=True)
        for article in st.session_state.news_articles:
            image_url = article.get('urlToImage', 'https://via.placeholder.com/300x150?text=No+Image')
            summary = generate_summary(article.get('description', 'No description available.'))
            st.markdown(
                f"""
                <div class="news-tile">
                    <img src="{image_url}" class="news-image" alt="News Image">
                    <div class="news-content">
                        <div class="news-title">{article['title']}</div>
                        <div class="news-source">{article['source']['name']} | {article['publishedAt'][:10]}</div>
                        <div class="news-summary">{summary}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
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
                    await fetch('https://your-server.herokuapp.com/subscribe', {{
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