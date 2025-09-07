# Configuration file for Operations Bot
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # OneDrive Configuration
    ONEDRIVE_BASE_FOLDER = os.getenv("ONEDRIVE_BASE_FOLDER", "Operations")
    ONEDRIVE_ACCESS_TOKEN = os.getenv("ONEDRIVE_ACCESS_TOKEN", "")
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # gemini, huggingface, openai
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "")
    LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "")  # Optional custom endpoint
    
    # Bot Configuration
    BOT_NAME = "Operations Bot"
    BOT_DESCRIPTION = "AI-powered assistant for operations team data analysis"
    
    # Data Categories
    DATA_CATEGORIES = [
        "RRF",
        "Training", 
        "Utilization",
        "Bench Report",
        "Certification List",
        "Account wise information",
        "Overall TSC GTs information"
    ]
    
    # File Processing
    SUPPORTED_FILE_TYPES = [".xlsx", ".xls", ".csv", ".pdf", ".pptx", ".ppt"]
    MAX_FILE_SIZE_MB = 50
    
    # Cache Settings
    CACHE_DURATION_HOURS = 24
    ENABLE_CACHING = True

# Validate configuration
def validate_config():
    """Validate that required configuration is present"""
    errors = []
    
    if not Config.ONEDRIVE_ACCESS_TOKEN:
        errors.append("ONEDRIVE_ACCESS_TOKEN is required")
    
    if not Config.LLM_API_KEY:
        errors.append("LLM_API_KEY is required")
    
    if not Config.ONEDRIVE_BASE_FOLDER:
        errors.append("ONEDRIVE_BASE_FOLDER is required")
    
    if Config.LLM_PROVIDER not in ["gemini", "huggingface", "openai"]:
        errors.append("LLM_PROVIDER must be one of: gemini, huggingface, openai")
    
    return errors

def get_default_model(provider: str) -> str:
    """Get default model for the given provider"""
    defaults = {
        "gemini": "gemini-1.5-flash",
        "huggingface": "microsoft/DialoGPT-large",
        "openai": "gpt-3.5-turbo"
    }
    return defaults.get(provider, "gemini-1.5-flash")
