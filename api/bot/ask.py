from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://opsbot-mu.vercel.app",
        "https://*.vercel.app",
        "https://*.vercel.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class BotQuestionRequest(BaseModel):
    question: str

@app.post("/")
async def ask_bot(req: BotQuestionRequest):
    """Answer bot questions"""
    try:
        if not req.question.strip():
            raise HTTPException(status_code=400, detail="Question is required")
        
        return {
            "answer": f"I received your question: '{req.question}'. The Operations Bot is running in simplified mode on Vercel. For full functionality, please ensure all dependencies are properly configured.",
            "confidence": 0.8,
            "sources": ["Operations Bot API"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bot query failed: {str(e)}")

# Vercel serverless function handler
handler = app
