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
async def get_dashboard():
    """Get dashboard data"""
    try:
        return {
            "active_rrfs": 0,
            "bench_resources": 0,
            "active_projects": 0,
            "trainees": 0,
            "recent_rrf_updates": [],
            "training_progress": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

# Vercel serverless function handler
handler = app
