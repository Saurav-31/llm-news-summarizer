from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
import time
from datetime import datetime, timedelta
import json
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Validate required API keys
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY environment variable is not set. Please set it in your .env file or environment.")

# Ollama configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Using localhost since Ollama runs in the same container
OLLAMA_MODEL = "mistral"  # Using Mistral model, which is good for summarization

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TrendSummary(BaseModel):
    trend: str
    summary: str
    article_count: int
    error: str = None

def check_ollama_connection():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except:
        return False

def get_trending_topics():
    try:
        # Get top headlines from NewsAPI
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'country': 'us',
            'pageSize': 2  # Increased to 5 articles
        }
        
        headers = {
            'X-Api-Key': NEWS_API_KEY
        }
        
        print(f"Making request to NewsAPI with key: {NEWS_API_KEY[:5]}...")
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"NewsAPI response status: {data.get('status')}")
        print(f"Total results: {data.get('totalResults')}")
        
        articles = data.get('articles', [])
        print(f"Number of articles received: {len(articles)}")
        
        if not articles:
            print("No articles found in response")
            return []
            
        return articles
    except Exception as e:
        print(f"Error getting news: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response content: {e.response.text}")
        return []

def generate_summary_with_ollama(text: str) -> str:
    try:
        # Check if Ollama is running
        if not check_ollama_connection():
            raise ConnectionError("Ollama is not running. Please start Ollama and try again.")
        
        prompt = f"Please provide a concise summary of the following text in 2-3 sentences:\n\n{text}"
        
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=30  # Add timeout to prevent hanging
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', 'No summary available')
    except ConnectionError as e:
        print(f"Ollama connection error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error generating summary with Ollama: {str(e)}")
        raise

@app.get("/api/trends")
async def get_trends():
    try:
        # Get trending topics from NewsAPI
        articles = get_trending_topics()
        
        if not articles:
            print("No articles returned from get_trending_topics")
            return [TrendSummary(
                trend="No trends available",
                summary="Unable to fetch news at this time. Please try again later.",
                article_count=0,
                error="No articles could be retrieved"
            )]
        
        # Process articles and generate summaries
        trend_summaries = []
        for article in articles:
            try:
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                
                print(f"Processing article: {title}")
                
                if title and (description or content):
                    try:
                        # Try to generate summary using Ollama
                        full_text = f"Title: {title}\nDescription: {description}\nContent: {content}"
                        print("Generating summary with Ollama...")
                        summary = generate_summary_with_ollama(full_text)
                        print(f"Generated summary: {summary[:100]}...")
                    except ConnectionError as e:
                        print(f"Ollama connection error: {str(e)}")
                        # If Ollama is not available, use the article description
                        summary = description or content or "No summary available"
                        print("Warning: Using article description as fallback (Ollama not available)")
                    except Exception as e:
                        print(f"Error generating summary: {str(e)}")
                        # For other errors, use the article description
                        summary = description or content or "No summary available"
                        print(f"Warning: Using article description as fallback (Error: {str(e)})")
                    
                    trend_summaries.append(TrendSummary(
                        trend=title,
                        summary=summary,
                        article_count=1
                    ))
            except Exception as e:
                print(f"Error processing article: {str(e)}")
                trend_summaries.append(TrendSummary(
                    trend=title if title else "Unknown",
                    summary="",
                    article_count=0,
                    error=f"Error processing article: {str(e)}"
                ))
        
        if not trend_summaries:
            print("No trend summaries generated")
            return [TrendSummary(
                trend="No trends available",
                summary="Unable to fetch news at this time. Please try again later.",
                article_count=0,
                error="No articles could be retrieved"
            )]
        
        print(f"Returning {len(trend_summaries)} trend summaries")
        return trend_summaries
    
    except Exception as e:
        print(f"Error in get_trends: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching trends: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 