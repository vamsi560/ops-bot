# Operations Bot Logic
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from config import Config, get_default_model
from onedrive import OneDriveClient
from extractor import extract_file, get_file_summary
from llm import LLMClient

class OperationsBot:
    def __init__(self):
        # Initialize LLM client with provider configuration
        model = Config.LLM_MODEL or get_default_model(Config.LLM_PROVIDER)
        self.llm_client = LLMClient(
            provider=Config.LLM_PROVIDER,
            api_key=Config.LLM_API_KEY,
            model=model,
            endpoint=Config.LLM_ENDPOINT
        )
        self.onedrive_client = OneDriveClient(Config.ONEDRIVE_ACCESS_TOKEN)
        self.cache = {}
        self.last_scan = None
        
    async def scan_all_data(self) -> Dict[str, Any]:
        """Scan all categories and extract data"""
        if self._is_cache_valid():
            return self.cache.get('scan_data', {})
        
        scan_results = {}
        total_files = 0
        
        for category in Config.DATA_CATEGORIES:
            try:
                folder_path = f"{Config.ONEDRIVE_BASE_FOLDER}/{category}"
                files = self.onedrive_client.list_files(folder_path)
                
                category_data = {
                    "folder_path": folder_path,
                    "files": files,
                    "file_count": len(files),
                    "last_scan": datetime.now().isoformat()
                }
                
                # Extract data from files
                extracted_data = {}
                for file_info in files:
                    try:
                        # Download and extract file
                        temp_path = f"temp_{file_info['id']}"
                        self.onedrive_client.download_file(file_info['id'], temp_path)
                        
                        # Get file summary first
                        summary = get_file_summary(temp_path)
                        extracted_data[file_info['name']] = {
                            "file_info": file_info,
                            "summary": summary
                        }
                        
                        # Clean up temp file
                        import os
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                            
                    except Exception as e:
                        extracted_data[file_info['name']] = {
                            "file_info": file_info,
                            "error": str(e)
                        }
                
                category_data["extracted_data"] = extracted_data
                scan_results[category] = category_data
                total_files += len(files)
                
            except Exception as e:
                scan_results[category] = {
                    "folder_path": f"{Config.ONEDRIVE_BASE_FOLDER}/{category}",
                    "files": [],
                    "file_count": 0,
                    "error": str(e),
                    "last_scan": datetime.now().isoformat()
                }
        
        # Cache the results
        self.cache['scan_data'] = scan_results
        self.cache['last_scan'] = datetime.now()
        self.last_scan = datetime.now()
        
        return {
            "scan_results": scan_results,
            "summary": {
                "total_categories": len(Config.DATA_CATEGORIES),
                "total_files": total_files,
                "last_scan": datetime.now().isoformat(),
                "categories": {cat: scan_results[cat]["file_count"] for cat in scan_results}
            }
        }
    
    async def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using the bot's knowledge base"""
        try:
            # Get current data
            data = await self.scan_all_data()
            
            # Prepare context for LLM
            context = self._prepare_context(data, question)
            
            # Generate response using LLM
            response = self.llm_client.query(question, context)
            
            return {
                "question": question,
                "answer": response,
                "timestamp": datetime.now().isoformat(),
                "data_sources": self._get_data_sources(data),
                "confidence": "high"  # Could be calculated based on data availability
            }
            
        except Exception as e:
            return {
                "question": question,
                "answer": f"I'm sorry, I encountered an error while processing your question: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _prepare_context(self, data: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Prepare context for LLM based on question and available data"""
        context = {
            "bot_info": {
                "name": Config.BOT_NAME,
                "description": Config.BOT_DESCRIPTION,
                "categories": Config.DATA_CATEGORIES
            },
            "data_summary": data.get("summary", {}),
            "available_data": {}
        }
        
        # Add relevant data based on question keywords
        question_lower = question.lower()
        
        for category, category_data in data.get("scan_results", {}).items():
            if self._is_category_relevant(question_lower, category):
                context["available_data"][category] = {
                    "file_count": category_data.get("file_count", 0),
                    "files": [f["name"] for f in category_data.get("files", [])],
                    "extracted_data": category_data.get("extracted_data", {})
                }
        
        return context
    
    def _is_category_relevant(self, question: str, category: str) -> bool:
        """Determine if a category is relevant to the question"""
        category_keywords = {
            "RRF": ["rrf", "resource", "request", "form"],
            "Training": ["training", "course", "learning", "skill"],
            "Utilization": ["utilization", "usage", "capacity", "workload"],
            "Bench Report": ["bench", "available", "idle", "resource"],
            "Certification List": ["certification", "cert", "qualification"],
            "Account wise information": ["account", "client", "customer"],
            "Overall TSC GTs information": ["tsc", "global", "team", "overall"]
        }
        
        keywords = category_keywords.get(category, [])
        return any(keyword in question for keyword in keywords)
    
    def _get_data_sources(self, data: Dict[str, Any]) -> List[str]:
        """Get list of data sources used for the answer"""
        sources = []
        for category, category_data in data.get("scan_results", {}).items():
            if category_data.get("file_count", 0) > 0:
                sources.append(f"{category} ({category_data['file_count']} files)")
        return sources
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not Config.ENABLE_CACHING or not self.last_scan:
            return False
        
        cache_duration = timedelta(hours=Config.CACHE_DURATION_HOURS)
        return datetime.now() - self.last_scan < cache_duration
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for visualization"""
        data = await self.scan_all_data()
        scan = data.get("scan_results", {})
        # Extract metrics
        active_rrfs = scan.get("RRF", {}).get("file_count", 0)
        bench_resources = scan.get("Bench Report", {}).get("file_count", 0)
        active_projects = scan.get("Utilization", {}).get("file_count", 0)
        trainees = scan.get("Training", {}).get("file_count", 0)

        # Recent RRF updates (mock: last 3 files from RRF)
        rrf_files = scan.get("RRF", {}).get("files", [])
        recent_rrf_updates = [
            {
                "role": f.get("name", "Unknown Role"),
                "client": f.get("client", "Unknown Client"),
                "status": "Open" if idx % 2 == 0 else "Filled"
            }
            for idx, f in enumerate(rrf_files[-3:])
        ]

        # Training progress (mock: last 3 files from Training)
        training_files = scan.get("Training", {}).get("files", [])
        training_progress = [
            {
                "title": f.get("name", "Unknown Training"),
                "trainees": f.get("trainees", 0),
                "status": "complete" if idx == 0 else ("progress" if idx == 1 else "done"),
                "progress": f"{75 - idx*30}% Complete" if idx < 2 else "Completed"
            }
            for idx, f in enumerate(training_files[-3:])
        ]

        return {
            "active_rrfs": active_rrfs,
            "bench_resources": bench_resources,
            "active_projects": active_projects,
            "trainees": trainees,
            "recent_rrf_updates": recent_rrf_updates,
            "training_progress": training_progress,
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_category_details(self, category: str) -> Dict[str, Any]:
        """Get detailed information about a specific category"""
        data = await self.scan_all_data()
        
        if category not in data.get("scan_results", {}):
            return {"error": f"Category '{category}' not found"}
        
        category_data = data["scan_results"][category]
        
        return {
            "category": category,
            "folder_path": category_data["folder_path"],
            "file_count": category_data["file_count"],
            "files": category_data.get("files", []),
            "extracted_data": category_data.get("extracted_data", {}),
            "last_scan": category_data.get("last_scan"),
            "status": "active" if category_data["file_count"] > 0 else "empty"
        }

# Global bot instance
bot = OperationsBot()
