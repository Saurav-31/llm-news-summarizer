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

# Load environment variables
load_dotenv()

# Configure API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Validate required API keys
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY environment variable is not set. Please set it in your .env file or environment.")

# Ollama configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Default Ollama API endpoint
OLLAMA_MODEL = "mistral"  # Using Mistral model, which is good for summarization

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
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
            'pageSize': 1  # Limit to 1 articles for free tier
        }
        
        # Use the API key in the URL as per NewsAPI documentation
        full_url = f"{url}?apiKey={NEWS_API_KEY}"
        
        response = requests.get(full_url, params=params)
        response.raise_for_status()
        
        articles = response.json().get('articles', [])
        return articles
    except Exception as e:
        print(f"Error getting news: {str(e)}")
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
            return [TrendSummary(
                trend="No trends available",
                summary="Unable to fetch trending topics at this time. Please try again later.",
                article_count=0,
                error="No trends could be retrieved"
            )]
        
        # Process articles and generate summaries
        trend_summaries = []
        for article in articles:
            try:
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                
                if title and (description or content):
                    try:
                        # Try to generate summary using Ollama
                        full_text = f"Title: {title}\nDescription: {description}\nContent: {content}"
                        summary = generate_summary_with_ollama(full_text)
                    except ConnectionError:
                        # If Ollama is not available, use the article description
                        summary = description or content or "No summary available"
                        print("Warning: Using article description as fallback (Ollama not available)")
                    except Exception as e:
                        # For other errors, use the article description
                        summary = description or content or "No summary available"
                        print(f"Warning: Using article description as fallback (Error: {str(e)})")
                    
                    trend_summaries.append(TrendSummary(
                        trend=title,
                        summary=summary,
                        article_count=1
                    ))
            except Exception as e:
                trend_summaries.append(TrendSummary(
                    trend=title if title else "Unknown",
                    summary="",
                    article_count=0,
                    error=f"Error processing article: {str(e)}"
                ))
        
        if not trend_summaries:
            return [TrendSummary(
                trend="No trends available",
                summary="Unable to fetch news at this time. Please try again later.",
                article_count=0,
                error="No articles could be retrieved"
            )]
        
        return trend_summaries
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching trends: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 