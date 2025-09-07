from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
def get_bot_status():
    """Get bot status"""
    try:
        return {
            "status": "healthy",
            "config_errors": [],
            "categories": ["RRF", "Training", "Projects", "Resources"],
            "last_scan": None,
            "cache_valid": False,
            "llm_provider": "gemini",
            "llm_model": "gemini-1.5-flash"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bot status: {str(e)}")

# Vercel serverless function handler
handler = app
