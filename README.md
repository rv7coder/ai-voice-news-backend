AI Voice News Backend (FastAPI)
Problem Statement
Reading long news articles daily is time-consuming. This project fetches real-time news, summarizes it using AI, and conTech Stack
FastAPI (Backend)
NewsAPI (News Source)
BART Transformer (Summarization)
gTTS (Text-to-Speech)
Git & GitHub (Version Control)
System Workflow
User → FastAPI Backend → NewsAPI → AI Summarizer → Text-to-Speech → Audio Output
Features
- Category-based news selection
- AI-powered summarization
- Voice-based news output
- Asynchronous processing
- Static audio hosting
API Endpoints
POST /select-field
GET /get-news/{user_id}
GET /summarize-news/{user_id}
GET /voice-summary/{user_id}
How to Run Locally
1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Set NEWS_API_KEY environment variable
5. Run using uvicorn
Future Enhancements
Multilingual support, user authentication, mobile frontend, cloud deployment, and advanced recommendation system.
Academic & Portfolio Value
Demonstrates real-world AI integration, backend system design, and use of pre-trained NLP models.
Author
Rudra Vedpathak
B.Tech – Artificial Intelligence & Machine Learning
