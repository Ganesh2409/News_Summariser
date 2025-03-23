# News Summarization and TTS Application

## Overview
This project is a web-based application that extracts news articles about a given company, analyzes the sentiment of the articles, and generates a Hindi text-to-speech (TTS) report.

## Features
✅ Extracts 10+ news articles using BeautifulSoup.
✅ Performs sentiment analysis on the content using Hugging Face's `transformers`.
✅ Generates a comparative sentiment report.
✅ Converts the summary report to Hindi speech using `gTTS`.
✅ User interface built with Streamlit.
✅ API development using FastAPI for modular communication.
✅ Deployed on Hugging Face Spaces.

---

## Project Structure
```
/Project_Root
├── app.py               # Main Streamlit application script
├── api.py               # FastAPI endpoints for data processing
├── utils.py             # Utility functions for scraping, sentiment analysis, etc.
├── requirements.txt     # Project dependencies
├── README.md            # Setup instructions and project documentation
```

---

## Installation Instructions
1. Clone the Repository:
   ```bash
   git clone <repository-link>
   cd Project_Root
   ```

2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run FastAPI Server:
   ```bash
   uvicorn api:app --reload
   ```

4. Run Streamlit Application:
   ```bash
   streamlit run app.py
   ```

5. Access the Application:
   - Open your browser and visit: `http://localhost:8501`

---

## Usage Instructions
1. Enter a **Company Name** in the input field.
2. Click on **Get Report** to:
   - View extracted news articles.
   - Analyze the sentiment distribution.
   - Listen to the Hindi audio summary.

---

## API Documentation
- **`/extract_news/{company}`** ➤ Extracts and displays 10 news articles.
- **`/analyze_sentiment/{company}`** ➤ Provides sentiment distribution and insights.
- **`/generate_tts/{company}`** ➤ Generates and plays a Hindi TTS report.

---

## Assumptions & Limitations
- Only non-JS web links are processed for news extraction.
- Some news articles may lack proper summaries due to incomplete scraping.

---

## Deployment
The project can be deployed on **Hugging Face Spaces** by following these steps:
- Create a new space on Hugging Face.
- Upload the entire codebase.
- Add the following in your `README.md` on Hugging Face:
  ```
  pip install -r requirements.txt
  uvicorn api:app --reload
  streamlit run app.py
  ```
## Querying System
- Users can enter a keyword or topic to filter news articles.
- The application will display only the articles that match the query.
- Sentiment analysis and comparative insights are provided for the filtered articles.

---

## Future Improvements
✅ Add query-based filtering for article topics.
✅ Enhance UI with interactive visualizations for better insights.
✅ Improve scraping logic to handle dynamic websites.
---



