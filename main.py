from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
import requests
from transformers import pipeline
from gtts import gTTS
import os
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from typing import Annotated
from enum import Enum

# Initial Setup
app = FastAPI(title = "AI Voice News Backend", version = "1.0")
NEWS_API_KEY = os.getenv("NEWS_API_KEY","099d13b6c62a4f858a8e4787f3dbacba")

# Ensure audio folder exists
os.makedirs("audio", exist_ok=True)

# In-memory store (for learning purpose)
user_preferences = {}

# Load AI model once at startup
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Data Models
class NewsField(str, Enum):
    Technology = "Technology"
    Business = "Business"
    Sports = "Sports"
    Health = "Health"
    Entertainment = "Entertainment"
    
class UserPreference(BaseModel):
    user_id: str = Field(..., example = "user_123")
    field: NewsField = Field(..., description="Select one of the available news categories") 
        
 
# Helper Functions
async def fetch_news(url: str, params: dict):
    return await run_in_threadpool(requests.get, url, params)
   
# Routes
@app.post("/select-field")
def select_field(preference: UserPreference):
    user_preferences[preference.user_id] = preference.field
    return {"status": "success", "user_id": preference.user_id, "selected_field": preference.field}

@app.get("/get-news/{user_id}")
async def get_news(user_id: str, page_size: Annotated[int, Query(ge = 1, le = 10)] = 5):
    field = user_preferences.get(user_id)
    if not field:
        return {"error": "no field selected for this user"}
    url = "https://newsapi.org/v2/top-headlines"
    params = {"category": field.value.lower(), "country": "us", "pageSize": page_size , "apiKey": NEWS_API_KEY}
    response = await fetch_news(url, params)
    data = response.json()
    
    articles = []
    for article in data.get("articles", []):
        articles.append({"title": article["title"], "description": article["description"]})
        
    return {"field": field, "articles": articles}    

@app.get("/summarize-news/{user_id}")
async def summarize_news (user_id):
    field = user_preferences.get(user_id)
    if not field:
        return {"error": "no field selected for this user"}
    url = "https://newsapi.org/v2/top-headlines"
    params = { "category": field.value.lower(), "country": "us", "pageSize": 3, "apiKey": NEWS_API_KEY}
    response = await fetch_news(url, params)
    data = response.json()
    
    summaries = []
    for article in data.get("articles", []):
        content = article.get("description")
        if len(content.split()) < 40:
            summaries.append(content)
            continue
        if not content:
            continue
        summary = await run_in_threadpool (lambda: summarizer(content, min_length = 25, do_sample = False)[0]["summary_text"])
        summaries.append(summary)
    
    return {"field": field, "summaries": summaries}    

@app.get("/voice-summary/{user_id}")
async def voice_summary(user_id: str):
    field = user_preferences.get(user_id)
    if not field:
        return {"error": "no field selected for this user"}
    url = "https://newsapi.org/v2/top-headlines"
    params = { "category": field.value.lower(), "country": "us", "pageSize": 1, "apiKey": NEWS_API_KEY}
    response = await fetch_news(url, params)
    data = response.json()
    articles = data.get("articles", [])
    if not articles:
        return {"error": "no articles found"}
    article = articles[0]
    text = article.get("description")
    if not text:
        return {"error", "no content to convert"}
    
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join("audio", filename)
    
    await run_in_threadpool(lambda: gTTS(text=text, lang="en").save(filepath))        
    
    return {"field": field, "audio_file": filename, "audio_url": f"http://127.0.0.1:8000/audio/{filename}"}

# Static Files
app.mount("/audio", StaticFiles(directory="audio"), name = "audio")
 