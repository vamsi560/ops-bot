"""
File Scanner for OneDrive/SharePoint
Scans folders and extracts data from Excel and Word files
"""

import os
import sys
import tempfile
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

try:
    from extractor import extract_file
    from token_manager import token_manager
    from config import Config
except ImportError as e:
    print(f"Import error: {e}")
    extract_file = None
    token_manager = None
    Config = None

class FileScanner:
    def __init__(self):
        self.base_folder = Config.ONEDRIVE_BASE_FOLDER if Config else ""
        self.supported_extensions = ['.xlsx', '.xls', '.csv', '.pdf', '.docx', '.doc']
        
    def scan_all_folders(self) -> Dict[str, Any]:
        """Scan all folders and extract data from files"""
        try:
            # Get valid token
            token = token_manager.get_valid_token() if token_manager else None
            if not token:
                return self._get_fallback_data("No valid token available")
            
            # Get all items in the base folder
            all_items = self._get_folder_contents(token, self.base_folder)
            if not all_items:
                return self._get_fallback_data("No items found in base folder")
            
            # Process all items (files and folders)
            result = {
                "scan_timestamp": datetime.now().isoformat(),
                "base_folder": self.base_folder,
                "total_items": len(all_items),
                "folders": [],
                "files": [],
                "extracted_data": {
                    "active_rrfs": 0,
                    "bench_resources": 0,
                    "active_projects": 0,
                    "trainees": 0,
                    "recent_rrf_updates": [],
                    "training_progress": []
                }
            }
            
            for item in all_items:
                if item.get('folder'):
                    # Process folder
                    folder_data = self._process_folder(token, item)
                    result["folders"].append(folder_data)
                else:
                    # Process file
                    file_data = self._process_file(token, item)
                    result["files"].append(file_data)
            
            # Extract data from all files
            self._extract_data_from_files(result["files"], result["extracted_data"])
            
            return result
            
        except Exception as e:
            return self._get_fallback_data(f"Scan failed: {str(e)}")
    
    def _get_folder_contents(self, token: str, folder_path: str) -> List[Dict]:
        """Get contents of a folder"""
        try:
            if "," in folder_path:
                # SharePoint site ID format
                url = f"https://graph.microsoft.com/v1.0/sites/{folder_path}/drive/root/children"
            else:
                # OneDrive format
                url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}:/children"
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                print(f"Failed to get folder contents: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting folder contents: {e}")
            return []
    
    def _process_folder(self, token: str, folder_item: Dict) -> Dict[str, Any]:
        """Process a folder and get its contents"""
        folder_name = folder_item.get('name', '')
        folder_id = folder_item.get('id', '')
        
        folder_data = {
            "name": folder_name,
            "id": folder_id,
            "files": [],
            "subfolders": []
        }
        
        try:
            # Get folder contents
            url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                contents = response.json().get('value', [])
                for item in contents:
                    if item.get('folder'):
                        folder_data["subfolders"].append(item.get('name', ''))
                    else:
                        file_data = self._process_file(token, item)
                        folder_data["files"].append(file_data)
            
        except Exception as e:
            print(f"Error processing folder {folder_name}: {e}")
        
        return folder_data
    
    def _process_file(self, token: str, file_item: Dict) -> Dict[str, Any]:
        """Process a file and extract its data"""
        file_name = file_item.get('name', '')
        file_id = file_item.get('id', '')
        file_size = file_item.get('size', 0)
        
        file_data = {
            "name": file_name,
            "id": file_id,
            "size": file_size,
            "extension": os.path.splitext(file_name)[1].lower(),
            "is_supported": os.path.splitext(file_name)[1].lower() in self.supported_extensions,
            "extracted_data": None,
            "error": None
        }
        
        # Only process supported files
        if file_data["is_supported"]:
            try:
                extracted = self._extract_file_data(token, file_id, file_name)
                file_data["extracted_data"] = extracted
            except Exception as e:
                file_data["error"] = str(e)
        
        return file_data
    
    def _extract_file_data(self, token: str, file_id: str, file_name: str) -> Dict[str, Any]:
        """Extract data from a file"""
        try:
            # Download file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
                temp_path = temp_file.name
            
            # Download file content
            url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                
                # Extract data using our extractor
                if extract_file:
                    extracted = extract_file(temp_path)
                else:
                    extracted = {"error": "File extractor not available"}
                
                # Clean up temp file
                os.unlink(temp_path)
                
                return extracted
            else:
                return {"error": f"Failed to download file: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Extraction failed: {str(e)}"}
    
    def _extract_data_from_files(self, files: List[Dict], extracted_data: Dict[str, Any]):
        """Extract relevant data from all files based on folder structure"""
        for file_data in files:
            if not file_data.get("extracted_data") or file_data.get("error"):
                continue
            
            file_name = file_data["name"].lower()
            extracted = file_data["extracted_data"]
            
            # Extract data based on file name and content
            if 'rrf' in file_name or 'request' in file_name:
                self._extract_rrf_data(extracted, extracted_data)
            elif 'training' in file_name or 'course' in file_name or 'certification' in file_name:
                self._extract_training_data(extracted, extracted_data)
            elif 'bench' in file_name or 'resource' in file_name:
                self._extract_bench_data(extracted, extracted_data)
            elif 'project' in file_name or 'allocation' in file_name or 'utilization' in file_name:
                self._extract_project_data(extracted, extracted_data)
            elif 'account' in file_name:
                self._extract_account_data(extracted, extracted_data)
    
    def _extract_rrf_data(self, extracted: Dict, result: Dict):
        """Extract RRF data from file"""
        if extracted.get("type") == "excel":
            sheets = extracted.get("sheets", {})
            for sheet_name, sheet_data in sheets.items():
                sheet_df_data = sheet_data.get("data", [])
                if sheet_df_data:
                    result["active_rrfs"] += len(sheet_df_data)
                    # Add recent RRFs
                    for row in sheet_df_data[:3]:
                        if isinstance(row, dict):
                            result["recent_rrf_updates"].append({
                                "role": row.get("Role", row.get("Position", "Unknown")),
                                "client": row.get("Client", row.get("Account", "Unknown")),
                                "status": row.get("Status", "Active"),
                                "date": row.get("Date", "2024-01-15")
                            })
    
    def _extract_training_data(self, extracted: Dict, result: Dict):
        """Extract training data from file"""
        if extracted.get("type") == "excel":
            sheets = extracted.get("sheets", {})
            for sheet_name, sheet_data in sheets.items():
                sheet_df_data = sheet_data.get("data", [])
                if sheet_df_data:
                    result["trainees"] += len(sheet_df_data)
                    # Add training progress
                    for row in sheet_df_data[:3]:
                        if isinstance(row, dict):
                            result["training_progress"].append({
                                "title": row.get("Course", row.get("Training", "Unknown")),
                                "trainees": row.get("Count", row.get("Trainees", 1)),
                                "status": row.get("Status", "In Progress"),
                                "progress": row.get("Progress", "50%")
                            })
    
    def _extract_bench_data(self, extracted: Dict, result: Dict):
        """Extract bench resource data from file"""
        if extracted.get("type") == "excel":
            sheets = extracted.get("sheets", {})
            for sheet_name, sheet_data in sheets.items():
                sheet_df_data = sheet_data.get("data", [])
                if sheet_df_data:
                    result["bench_resources"] += len(sheet_df_data)
    
    def _extract_project_data(self, extracted: Dict, result: Dict):
        """Extract project data from file"""
        if extracted.get("type") == "excel":
            sheets = extracted.get("sheets", {})
            for sheet_name, sheet_data in sheets.items():
                sheet_df_data = sheet_data.get("data", [])
                if sheet_df_data:
                    result["active_projects"] += len(sheet_df_data)
    
    def _extract_account_data(self, extracted: Dict, result: Dict):
        """Extract account details data from file"""
        if extracted.get("type") == "excel":
            sheets = extracted.get("sheets", {})
            for sheet_name, sheet_data in sheets.items():
                sheet_df_data = sheet_data.get("data", [])
                if sheet_df_data:
                    # Account details could contribute to various metrics
                    result["active_projects"] += len(sheet_df_data) // 2  # Half as projects
                    result["bench_resources"] += len(sheet_df_data) // 4  # Quarter as resources
    
    def _get_fallback_data(self, message: str) -> Dict[str, Any]:
        """Return fallback data when scanning fails"""
        return {
            "scan_timestamp": datetime.now().isoformat(),
            "base_folder": self.base_folder,
            "total_items": 0,
            "folders": [],
            "files": [],
            "extracted_data": {
                "active_rrfs": 0,
                "bench_resources": 0,
                "active_projects": 0,
                "trainees": 0,
                "recent_rrf_updates": [],
                "training_progress": []
            },
            "data_source": "fallback",
            "message": message
        }

# Global file scanner instance
file_scanner = FileScanner()
