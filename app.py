import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
from newsapi import NewsApiClient

load_dotenv()
st.set_page_config(page_title="🇮🇳 Indian News Feed", layout="wide")

# ✅ Load API Key
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
newsapi = NewsApiClient(api_key=NEWSAPI_KEY) if NEWSAPI_KEY else None

# 💾 Session state
if 'news_articles' not in st.session_state:
    st.session_state.news_articles = []
if 'last_query' not in st.session_state:
    st.session_state.last_query = "india"

# ✅ CSS: Fluid UI, glassmorphism, animation
st.markdown("""
    <style>
    html {
        scroll-behavior: smooth;
    }
    body {
        background: linear-gradient(to right, #eef2f3, #8e9eab);
    }
    .main-container {
        max-width: 1400px;
        margin: auto;
        padding: 1rem;
        animation: fadeIn 1.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .header {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(8px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
    }
    .header h1 {
        font-size: 2.6rem;
        color: #003366;
        margin: 0;
    }
    .header p {
        font-size: 1.1rem;
        color: #333;
        margin-top: 10px;
    }

    /* Horizontal scrolling container */
    .tile-grid {
        display: flex;
        flex-direction: row;
        gap: 25px;
        overflow-x: auto;
        padding-bottom: 1rem;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
        margin-bottom: 2rem;
        /* Center the tiles if there's extra space */
        justify-content: center;
        margin: 0 auto;
    }
    .tile-grid::-webkit-scrollbar {
        height: 10px;
    }
    .tile-grid::-webkit-scrollbar-thumb {
        background-color: #aaa;
        border-radius: 5px;
    }

    .news-tile {
        flex: 0 0 auto;
        width: 420px;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(6px);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        transition: transform 0.4s, box-shadow 0.3s ease;
        animation: fadeIn 0.6s ease-in;
        perspective: 800px;
    }
    .news-tile:hover {
        transform: rotateY(12deg) scale(1.05);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
    }

    .news-image {
        width: 100%;
        height: 180px;
        object-fit: cover;
    }
    .news-content {
        padding: 1.2rem;
    }
    .news-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #222;
    }
    .news-source {
        font-size: 0.85rem;
        color: #666;
        margin-top: 5px;
    }
    .news-summary {
        font-size: 0.95rem;
        color: #333;
        margin-top: 10px;
    }
    .stButton > button {
        background-color: #003366;
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #00509e;
        transform: scale(1.05);
    }
    @media (max-width: 600px) {
        .header h1 {
            font-size: 2rem;
        }
        .news-tile {
            width: 280px;
        }
        .news-image {
            height: 150px;
        }
    }
    </style>
    <div class="main-container">
""", unsafe_allow_html=True)

# ✨ Generate summary
def generate_summary(description):
    if not description:
        return "Summary not available."
    # Return at least 200 characters, or the entire description if shorter
    return description[:2000] + ("..." if len(description) > 200 else "")

# 🔄 Fetch News
@st.cache_data(ttl=300)
def fetch_news(query):
    if not newsapi:
        return []
    try:
        response = newsapi.get_everything(
            q=f"{query} india",
            language="en",
            sort_by="publishedAt",
            page_size=100
        )
        articles = response.get("articles", [])
        return sorted(articles, key=lambda x: x["publishedAt"], reverse=True)
    except Exception as e:
        st.error(f"API error: {e}")
        return []

# 🧠 Main app logic
def main():
    st.markdown("""
    <div class="header">
        <h1>🇮🇳 Indian News Feed</h1>
        <p>Real-time headlines</p>
    </div>
    """, unsafe_allow_html=True)

    query = st.text_input("Search news", value=st.session_state.last_query)
    #  = st.selectbox("Or select a ", ["india", "politics", "business", "stocks", "sports", "technology", "entertainment"])
    if st.button("Refresh Feed"):
        st.session_state.news_articles = []
        st.session_state.last_query = query

    # 🗞 Get news
    if not st.session_state.news_articles:
        with st.spinner("Loading news..."):
            st.session_state.news_articles = fetch_news(query)

    articles = st.session_state.news_articles
    if articles:
        st.markdown('<div class="tile-grid">', unsafe_allow_html=True)
        for article in articles:
            img = article.get("urlToImage") or "https://via.placeholder.com/400x200.png?text=No+Image"
            summary = generate_summary(article.get("description", ""))
            st.markdown(f"""
                <div class="news-tile">
                    <img src="{img}" class="news-image" />
                    <div class="news-content">
                        <div class="news-title">{article['title']}</div>
                        <div class="news-source">{article['source']['name']} | {article['publishedAt'][:10]}</div>
                        <div class="news-summary">{summary}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No news found. Try a different .")

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()