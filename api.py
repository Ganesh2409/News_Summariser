from fastapi import FastAPI, HTTPException
from utils import extract_news, comparative_analysis, generate_tts
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "News Summarization and TTS API is running"}

@app.get("/extract_news/{company}")
def get_news(company: str):
    try:
        articles = extract_news(company)
        return {"Company": company, "Articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze_sentiment/{company}")
def get_sentiment(company: str):
    try:
        articles = extract_news(company)
        sentiment_summary = comparative_analysis(articles)
        return {"Company": company, "Sentiment_Summary": sentiment_summary, "Articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate_tts/{company}")
def get_tts(company: str):
    try:
        articles = extract_news(company)
        sentiment_summary = comparative_analysis(articles)
        
        # Create Hindi summary text
        total_articles = sum(sentiment_summary.values())
        positive = sentiment_summary.get("Positive", 0)
        negative = sentiment_summary.get("Negative", 0)
        neutral = sentiment_summary.get("Neutral", 0)
        
        # Create Hindi report text
        hindi_report = f"""
        कंपनी {company} के समाचार विश्लेषण का सारांश:
        हमने कुल {total_articles} समाचार लेखों का विश्लेषण किया।
        इनमें से {positive} लेख सकारात्मक, {negative} लेख नकारात्मक, और {neutral} लेख तटस्थ पाए गए।
        """
        
        # Add a summary of a few key articles if available
        if articles and len(articles) > 0:
            hindi_report += "\nप्रमुख समाचार:\n"
            for i, article in enumerate(articles[:3]):  # Include top 3 articles
                hindi_report += f"{i+1}. {article['Title']}. "
                if article['Sentiment'] == "Positive":
                    hindi_report += "यह समाचार सकारात्मक है। "
                elif article['Sentiment'] == "Negative":
                    hindi_report += "यह समाचार नकारात्मक है। "
                else:
                    hindi_report += "यह समाचार तटस्थ है। "
        
        # Add overall sentiment summary
        if positive > negative and positive > neutral:
            hindi_report += "\nसमग्र रूप से, {company} के बारे में समाचार अधिकतर सकारात्मक हैं।"
        elif negative > positive and negative > neutral:
            hindi_report += f"\nसमग्र रूप से, {company} के बारे में समाचार अधिकतर नकारात्मक हैं।"
        else:
            hindi_report += f"\nसमग्र रूप से, {company} के बारे में समाचार मिश्रित या तटस्थ हैं।"
            
        audio_path = generate_tts(hindi_report)
        return {"Company": company, "Audio_File": audio_path, "Hindi_Text": hindi_report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)