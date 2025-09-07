from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import tempfile
import requests
from typing import Dict, List, Any

# Add the backend directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

try:
    from config import Config
    from onedrive import OneDriveClient
    from extractor import extract_file
except ImportError as e:
    print(f"Import error: {e}")
    Config = None
    OneDriveClient = None
    extract_file = None

class DataProcessor:
    def __init__(self):
        self.cache = {}
        self.cache_timestamp = None
        
    def get_real_data(self) -> Dict[str, Any]:
        """Get real data from OneDrive/SharePoint"""
        try:
            if not Config or not OneDriveClient:
                return self._get_fallback_data()
            
            # Check if we have access token
            if not Config.ONEDRIVE_ACCESS_TOKEN:
                return self._get_fallback_data()
            
            # Initialize OneDrive client
            client = OneDriveClient(Config.ONEDRIVE_ACCESS_TOKEN)
            
            # Get files from OneDrive/SharePoint
            files = client.list_files(Config.ONEDRIVE_BASE_FOLDER)
            
            if not files:
                return self._get_fallback_data()
            
            # Process files and extract data
            processed_data = self._process_files(client, files)
            
            return processed_data
            
        except Exception as e:
            print(f"Error getting real data: {e}")
            return self._get_fallback_data()
    
    def _process_files(self, client: OneDriveClient, files: List[Dict]) -> Dict[str, Any]:
        """Process files and extract relevant data"""
        data = {
            "active_rrfs": 0,
            "bench_resources": 0,
            "active_projects": 0,
            "trainees": 0,
            "recent_rrf_updates": [],
            "training_progress": [],
            "file_summaries": []
        }
        
        for file_info in files:
            if file_info.get('folder'):
                continue  # Skip folders
                
            file_name = file_info.get('name', '')
            file_id = file_info.get('id', '')
            
            # Check if it's a supported file type
            if not any(file_name.lower().endswith(ext) for ext in ['.xlsx', '.xls', '.csv', '.pdf']):
                continue
            
            try:
                # Download file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
                    temp_path = temp_file.name
                
                # Download file content
                url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
                headers = {"Authorization": f"Bearer {Config.ONEDRIVE_ACCESS_TOKEN}"}
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    with open(temp_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Extract data from file
                    if extract_file:
                        extracted = extract_file(temp_path)
                        data["file_summaries"].append({
                            "file_name": file_name,
                            "type": extracted.get("type", "unknown"),
                            "summary": extracted
                        })
                        
                        # Try to extract specific data based on file name
                        self._extract_specific_data(file_name, extracted, data)
                    
                    # Clean up temp file
                    os.unlink(temp_path)
                    
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")
                continue
        
        return data
    
    def _extract_specific_data(self, file_name: str, extracted_data: Dict, data: Dict):
        """Extract specific data based on file name patterns"""
        file_lower = file_name.lower()
        
        try:
            if 'rrf' in file_lower or 'request' in file_lower:
                # Extract RRF data
                if extracted_data.get("type") == "excel":
                    sheets = extracted_data.get("sheets", {})
                    for sheet_name, sheet_data in sheets.items():
                        sheet_df_data = sheet_data.get("data", [])
                        if sheet_df_data:
                            data["active_rrfs"] += len(sheet_df_data)
                            # Add recent RRFs
                            for row in sheet_df_data[:3]:  # Take first 3
                                if isinstance(row, dict):
                                    data["recent_rrf_updates"].append({
                                        "role": row.get("Role", row.get("Position", "Unknown")),
                                        "client": row.get("Client", row.get("Account", "Unknown")),
                                        "status": row.get("Status", "Active"),
                                        "date": row.get("Date", "2024-01-15")
                                    })
            
            elif 'training' in file_lower or 'course' in file_lower:
                # Extract training data
                if extracted_data.get("type") == "excel":
                    sheets = extracted_data.get("sheets", {})
                    for sheet_name, sheet_data in sheets.items():
                        sheet_df_data = sheet_data.get("data", [])
                        if sheet_df_data:
                            data["trainees"] += len(sheet_df_data)
                            # Add training progress
                            for row in sheet_df_data[:3]:  # Take first 3
                                if isinstance(row, dict):
                                    data["training_progress"].append({
                                        "title": row.get("Course", row.get("Training", "Unknown")),
                                        "trainees": row.get("Count", row.get("Trainees", 1)),
                                        "status": row.get("Status", "In Progress"),
                                        "progress": row.get("Progress", "50%")
                                    })
            
            elif 'bench' in file_lower or 'resource' in file_lower:
                # Extract bench resource data
                if extracted_data.get("type") == "excel":
                    sheets = extracted_data.get("sheets", {})
                    for sheet_name, sheet_data in sheets.items():
                        sheet_df_data = sheet_data.get("data", [])
                        if sheet_df_data:
                            data["bench_resources"] += len(sheet_df_data)
            
            elif 'project' in file_lower:
                # Extract project data
                if extracted_data.get("type") == "excel":
                    sheets = extracted_data.get("sheets", {})
                    for sheet_name, sheet_data in sheets.items():
                        sheet_df_data = sheet_data.get("data", [])
                        if sheet_df_data:
                            data["active_projects"] += len(sheet_df_data)
                            
        except Exception as e:
            print(f"Error extracting specific data from {file_name}: {e}")
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Return fallback data when OneDrive is not available"""
        return {
            "active_rrfs": 0,
            "bench_resources": 0,
            "active_projects": 0,
            "trainees": 0,
            "recent_rrf_updates": [],
            "training_progress": [],
            "file_summaries": [],
            "data_source": "fallback",
            "message": "OneDrive connection not available. Please check configuration."
        }

# Global data processor instance
data_processor = DataProcessor()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Get real data from OneDrive
            real_data = data_processor.get_real_data()
            self.wfile.write(json.dumps(real_data).encode())
        except Exception as e:
            error_response = {
                "error": f"Failed to process data: {str(e)}",
                "active_rrfs": 0,
                "bench_resources": 0,
                "active_projects": 0,
                "trainees": 0,
                "recent_rrf_updates": [],
                "training_progress": []
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
