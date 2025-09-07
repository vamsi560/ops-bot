
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
from bot import bot
from config import Config, validate_config
import asyncio

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

@app.get("/api/")
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
@app.post("/api/bot/ask")
async def ask_bot(req: BotQuestionRequest):
    try:
        if not req.question.strip():
            raise HTTPException(status_code=400, detail="Question is required")
        
        response = await bot.answer_question(req.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bot query failed: {str(e)}")

# Get dashboard data
@app.get("/api/bot/dashboard")
async def get_dashboard():
    try:
        data = await bot.get_dashboard_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

# Get category details
@app.post("/api/bot/category")
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
@app.post("/api/bot/scan")
async def scan_data():
    try:
        data = await bot.scan_all_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scan data: {str(e)}")

# Get bot status
@app.get("/api/bot/status")
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
@app.get("/api/bot/models")
def get_available_models():
    try:
        from llm import LLMClient
        client = LLMClient(Config.LLM_PROVIDER, Config.LLM_API_KEY)
        return {
            "current_provider": Config.LLM_PROVIDER,
            "current_model": Config.LLM_MODEL or get_default_model(Config.LLM_PROVIDER),
            "available_models": client.get_available_models()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")

# Vercel serverless function handler
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)