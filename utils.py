import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from gtts import gTTS
import os
import re
import time

# News Extraction Function
def extract_news(company):
    # Use RSS feed for more reliable data
    url = f"https://news.google.com/rss/search?q={company}&hl=en-IN&gl=IN&ceid=IN:en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    # Parse as XML since we're using RSS feed
    soup = BeautifulSoup(response.text, 'xml')
    
    articles = []
    items = soup.find_all('item')
    
    for item in items[:10]:  # Limit to 10 articles
        title = item.find('title').text if item.find('title') else "No Title"
        
        # Get description
        description = item.find('description')
        if description:
            full_text = description.text
            
            # Clean up HTML from description
            full_text = re.sub(r'<[^>]+>', '', full_text)
            
            # Try to extract just the first sentence or article description
            parts = re.split(r'\s+(?=[A-Z][a-z]+\s*(?:Times|Post|News|Journal|Today|Standard|Express|Telegraph|Mail|Guardian|Independent|Star|Sun|Mirror|Chronicle|Gazette|Herald|Tribune|Observer|Daily|Weekly))', full_text, 1)
            
            if len(parts) > 1:
                summary = parts[0].strip()
            else:
                # If we couldn't split by publication name, try to get the first sentence
                sentences = re.split(r'(?<=[.!?])\s+', full_text, 1)
                summary = sentences[0].strip()
                
            # Fallback if summary is too short
            if len(summary) < 20:
                summary = full_text[:200] + "..." if len(full_text) > 200 else full_text
        else:
            summary = "No Summary Available"
            
        # Get link if available
        link = item.find('link').text if item.find('link') else ""
        
        # Extract publication date if available
        pub_date = item.find('pubDate')
        date = pub_date.text if pub_date else "Unknown Date"
        
        articles.append({
            "Title": title, 
            "Summary": summary, 
            "Link": link,
            "Date": date
        })
    
    # If no articles found with RSS, try alternate method (this is a backup)
    if not articles:
        url = f"https://news.google.com/search?q={company}&hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find article elements with different selectors
        article_elements = soup.select('div[class*="NiLAwe"]') or soup.select('article') or soup.select('.ipQwMb')
        
        for element in article_elements[:10]:
            # Look for title in various possible elements
            title_elem = element.select_one('h3 a') or element.select_one('h4 a') or element.select_one('a[class*="DY5T1d"]')
            title = title_elem.text if title_elem else "No Title"
            
            # Look for summary in various possible elements
            summary_elem = element.select_one('span[class*="xBbh9"]') or element.select_one('div[class*="xBbh9"]')
            summary = summary_elem.text if summary_elem else "No Summary Available"
            
            # Get link if available
            link_elem = element.select_one('a')
            link = link_elem.get('href', '') if link_elem else ""
            if link and not link.startswith('http'):
                link = f"https://news.google.com{link}"
                
            articles.append({
                "Title": title, 
                "Summary": summary, 
                "Link": link,
                "Date": "Unknown Date"
            })
    
    return articles

# Initialize sentiment analysis pipeline only once
_sentiment_pipeline = None
def get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline("sentiment-analysis")
    return _sentiment_pipeline

# Extract key topics from text using simple keyword extraction
def extract_topics(text, company_name):
    # Common business and financial terms to look for
    business_terms = [
        "profit", "revenue", "sales", "growth", "decline", "stock", "share", "market",
        "investment", "investor", "CEO", "executive", "launch", "product", "service",
        "expansion", "acquisition", "merger", "partnership", "earnings", "quarter",
        "financial", "report", "technology", "innovation", "development", "customer",
        "user", "regulation", "compliance", "lawsuit", "legal", "announce", "announce",
        "release", "future", "strategy", "plan", "competition", "competitor"
    ]
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    company_lower = company_name.lower()
    
    # Remove the company name from consideration (it will be in most articles)
    topics = set()
    
    # Find business terms in the text
    for term in business_terms:
        if term in text_lower and term != company_lower:
            topics.add(term.capitalize())
            
    # If we found at least 2 topics, return them
    if len(topics) >= 2:
        return list(topics)
    
    # Otherwise, find the most common words (excluding stopwords)
    stopwords = ["the", "and", "a", "in", "to", "of", "is", "that", "it", "with", "as", "for", 
                "was", "on", "are", "be", "by", "at", "an", "this", "have", "from", "or", "but", "not", "what", "all"]
    
    # Simple tokenization, filtering, and counting
    words = re.findall(r'\b\w+\b', text_lower)
    word_counts = {}
    
    for word in words:
        if word not in stopwords and word != company_lower and len(word) > 3:
            word_counts[word] = word_counts.get(word, 0) + 1
            
    # Get the top 3 most common words
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    additional_topics = [word.capitalize() for word, _ in top_words]
    
    # Combine with any business terms we found
    return list(topics) + additional_topics

# Sentiment Analysis Function with retry mechanism
def analyze_sentiment(text):
    if not text or text == "No Summary Available":
        return "Neutral"  # Default to neutral for empty or missing text
        
    try:
        # Get or initialize sentiment pipeline
        sentiment_pipeline = get_sentiment_pipeline()
        
        # Limit text length to avoid errors, but ensure we have enough context
        text_to_analyze = text[:512] if len(text) > 512 else text
        
        # Try sentiment analysis with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = sentiment_pipeline(text_to_analyze)[0]
                
                # Map the sentiment to the expected format
                if result["label"] == "POSITIVE" or result["label"] == "LABEL_1":
                    return "Positive"
                elif result["label"] == "NEGATIVE" or result["label"] == "LABEL_0":
                    return "Negative"
                else:
                    return "Neutral"
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Retrying sentiment analysis. Error: {str(e)}")
                    time.sleep(1)  # Wait before retrying
                else:
                    raise
                    
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return "Neutral"  # Default to neutral on error

# Comparative Analysis Function
def comparative_analysis(articles):
    sentiment_summary = {"Positive": 0, "Negative": 0, "Neutral": 0}
    
    for article in articles:
        # Use title for sentiment if summary is not available
        text_to_analyze = article["Summary"]
        if text_to_analyze == "No Summary Available" and article["Title"] != "No Title":
            text_to_analyze = article["Title"]
            
        sentiment = analyze_sentiment(text_to_analyze)
        sentiment_summary[sentiment] += 1
        article["Sentiment"] = sentiment
        
        # Extract topics from the article text
        article_text = f"{article['Title']} {article['Summary']}"
        article["Topics"] = extract_topics(article_text, article.get("Title", "").split()[0])
        
    return sentiment_summary

# Text-to-Speech Conversion
def generate_tts(text, language='hi'):
    try:
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        output_path = os.path.join('output', 'output.mp3')
        
        # Generate TTS
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error generating TTS: {str(e)}")
        return None