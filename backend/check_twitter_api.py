import os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

import requests

url = "https://newsapi.org/v2/top-headlines?country=us&pageSize=10"
headers = {"Authorization": "Bearer YOUR_API_KEY"}  # <-- NewsAPI expects it in query param, not headers

# Correct usage
response = requests.get(f"{url}&apiKey={NEWS_API_KEY}")
print(response.json())