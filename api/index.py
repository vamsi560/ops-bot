from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import only what we need for basic functionality
from config import Config, validate_config
import asyncio

def get_default_model(provider):
    """Get default model for the given provider"""
    defaults = {
        "gemini": "gemini-1.5-flash",
        "huggingface": "microsoft/DialoGPT-medium",
        "openai": "gpt-3.5-turbo"
    }
    return defaults.get(provider, "gemini-1.5-flash")

# Simplified bot implementation for Vercel
class SimpleBot:
    def __init__(self):
        self.last_scan = None
    
    async def answer_question(self, question):
        """Simple question answering"""
        return {
            "answer": f"I received your question: '{question}'. The Operations Bot is running in simplified mode on Vercel. For full functionality, please ensure all dependencies are properly configured.",
            "confidence": 0.8,
            "sources": ["Operations Bot API"]
        }
    
    async def get_dashboard_data(self):
        """Get dashboard data"""
        return {
            "active_rrfs": 0,
            "bench_resources": 0,
            "active_projects": 0,
            "trainees": 0,
            "recent_rrf_updates": [],
            "training_progress": []
        }
    
    async def get_category_details(self, category):
        """Get category details"""
        return {
            "category": category,
            "data": [],
            "message": f"Category '{category}' details would be available with full backend implementation."
        }
    
    async def scan_all_data(self):
        """Scan all data"""
        return {
            "message": "Data scanning would be available with full backend implementation.",
            "scanned_categories": [],
            "total_files": 0
        }
    
    def _is_cache_valid(self):
        """Check if cache is valid"""
        return False

# Initialize simple bot
bot = SimpleBot()

app = FastAPI()

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://opsbot-mu.vercel.app",  # Your specific frontend URL
        "https://*.vercel.app",  # All Vercel deployments
        "https://*.vercel.com"   # Vercel custom domains
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class BotQuestionRequest(BaseModel):
    question: str

class CategoryRequest(BaseModel):
    category: str

@app.get("/")
def read_root():
    # Validate configuration on startup
    config_errors = validate_config()
    
    return {
        "message": f"{Config.BOT_NAME} is running.",
        "description": Config.BOT_DESCRIPTION,
        "status": "healthy" if not config_errors else "configuration_error",
        "version": "2.0.0",
        "config_errors": config_errors,
        "categories": Config.DATA_CATEGORIES
    }

# Bot Question Endpoint - Main interface for users
@app.post("/bot/ask")
async def ask_bot(req: BotQuestionRequest):
    try:
        if not req.question.strip():
            raise HTTPException(status_code=400, detail="Question is required")
        
        response = await bot.answer_question(req.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bot query failed: {str(e)}")

# Get dashboard data
@app.get("/bot/dashboard")
async def get_dashboard():
    try:
        data = await bot.get_dashboard_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

# Get category details
@app.post("/bot/category")
async def get_category_details(req: CategoryRequest):
    try:
        if not req.category:
            raise HTTPException(status_code=400, detail="Category is required")
        
        if req.category not in Config.DATA_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category. Available: {Config.DATA_CATEGORIES}")
        
        data = await bot.get_category_details(req.category)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category details: {str(e)}")

# Scan all data (admin endpoint)
@app.post("/bot/scan")
async def scan_data():
    try:
        data = await bot.scan_all_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scan data: {str(e)}")

# Get bot status
@app.get("/bot/status")
def get_bot_status():
    try:
        config_errors = validate_config()
        return {
            "status": "healthy" if not config_errors else "configuration_error",
            "config_errors": config_errors,
            "categories": Config.DATA_CATEGORIES,
            "last_scan": bot.last_scan.isoformat() if bot.last_scan else None,
            "cache_valid": bot._is_cache_valid(),
            "llm_provider": Config.LLM_PROVIDER,
            "llm_model": Config.LLM_MODEL or get_default_model(Config.LLM_PROVIDER)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bot status: {str(e)}")

# Get available LLM models
@app.get("/bot/models")
def get_available_models():
    try:
        return {
            "current_provider": Config.LLM_PROVIDER,
            "current_model": Config.LLM_MODEL or get_default_model(Config.LLM_PROVIDER),
            "available_models": {
                "gemini": ["gemini-1.5-flash", "gemini-1.5-pro"],
                "huggingface": ["microsoft/DialoGPT-medium"],
                "openai": ["gpt-3.5-turbo", "gpt-4"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")

# Vercel serverless function handler
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
