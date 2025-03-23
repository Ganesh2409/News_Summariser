import streamlit as st
import requests
import time

API_BASE_URL = "http://localhost:8000"

st.title("News Summarization and TTS Application")

# Add a status indicator for API connection
try:
    response = requests.get(f"{API_BASE_URL}/")
    if response.status_code == 200:
        st.success("✅ Connected to API server")
    else:
        st.error("❌ API server is not responding correctly")
except requests.exceptions.ConnectionError:
    st.error("❌ Cannot connect to API server. Please make sure it's running on http://localhost:8000")

company = st.text_input("Enter Company Name:")

if st.button("Get Report"):
    if not company:
        st.warning("Please enter a company name")
    else:
        with st.spinner("Fetching news and analyzing sentiment..."):
            try:
                # Extract News
                news_response = requests.get(f"{API_BASE_URL}/extract_news/{company}")
                if news_response.status_code == 200:
                    news_data = news_response.json()
                    articles = news_data.get("Articles", [])
                    
                    # Display News Articles
                    st.subheader(f"News Articles for {company}")
                    if articles:
                        for i, article in enumerate(articles):
                            with st.expander(f"{i+1}. {article['Title']}"):
                                st.write(f"**Summary:** {article['Summary']}")
                                
                                # Display link if available
                                if article.get('Link'):
                                    st.write(f"**Source:** [Read more]({article['Link']})")
                                
                                # Add sentiment tag with color
                                if article.get('Sentiment'):
                                    sentiment = article.get('Sentiment')
                                    if sentiment == "Positive":
                                        st.success(f"Sentiment: {sentiment}")
                                    elif sentiment == "Negative":
                                        st.error(f"Sentiment: {sentiment}")
                                    else:
                                        st.info(f"Sentiment: {sentiment}")
                    else:
                        st.info("No articles found for this company")

                    # Sentiment Analysis
                    sentiment_response = requests.get(f"{API_BASE_URL}/analyze_sentiment/{company}")
                    if sentiment_response.status_code == 200:
                        sentiment_data = sentiment_response.json()
                        sentiment_summary = sentiment_data.get("Sentiment_Summary", {})
                        
                        st.subheader("Sentiment Analysis")
                        
                        # Create a more visual display of sentiment
                        total_articles = sum(sentiment_summary.values())
                        
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            positive = sentiment_summary.get("Positive", 0)
                            positive_pct = (positive / total_articles * 100) if total_articles > 0 else 0
                            st.metric("Positive", f"{positive} ({positive_pct:.1f}%)")
                        with col2:
                            neutral = sentiment_summary.get("Neutral", 0)
                            neutral_pct = (neutral / total_articles * 100) if total_articles > 0 else 0
                            st.metric("Neutral", f"{neutral} ({neutral_pct:.1f}%)")
                        with col3:
                            negative = sentiment_summary.get("Negative", 0)
                            negative_pct = (negative / total_articles * 100) if total_articles > 0 else 0
                            st.metric("Negative", f"{negative} ({negative_pct:.1f}%)")
                        
                        # Add a simple bar chart
                        st.bar_chart({
                            "Sentiment": ["Positive", "Neutral", "Negative"],
                            "Count": [positive, neutral, negative]
                        }, x="Sentiment", y="Count")
                    else:
                        st.error(f"Error in sentiment analysis: {sentiment_response.text}")

                    # Generate TTS Report
                    with st.spinner("Generating Hindi audio summary..."):
                        tts_response = requests.get(f"{API_BASE_URL}/generate_tts/{company}")
                        if tts_response.status_code == 200:
                            tts_data = tts_response.json()
                            audio_path = tts_data.get("Audio_File", "")
                            hindi_text = tts_data.get("Hindi_Text", "")

                            st.subheader("Hindi Summary")
                            
                            # Display Hindi text
                            if hindi_text:
                                st.text_area("Hindi Text", hindi_text, height=150)
                            
                            # Display audio player
                            if audio_path:
                                st.audio(audio_path, format='audio/mp3')
                            else:
                                st.error("Failed to generate audio summary")
                        else:
                            st.error(f"Error in TTS generation: {tts_response.text}")
                else:
                    st.error(f"Error fetching news: {news_response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")