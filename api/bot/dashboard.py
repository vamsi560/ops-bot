from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

try:
    from config import Config
    from file_scanner import file_scanner
    from token_manager import token_manager
except ImportError:
    Config = None
    file_scanner = None
    token_manager = None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Use the file scanner to get real data from OneDrive
            if file_scanner:
                scan_result = file_scanner.scan_all_folders()
                
                # Extract the dashboard data from scan result
                extracted_data = scan_result["extracted_data"]
                dashboard_data = {
                    "active_rrfs": extracted_data["active_rrfs"],
                    "bench_resources": extracted_data["bench_resources"],
                    "active_projects": extracted_data["active_projects"],
                    "trainees": extracted_data["trainees"],
                    "recent_rrf_updates": extracted_data["recent_rrf_updates"],
                    "training_progress": extracted_data["training_progress"],
                    "data_source": scan_result.get("data_source", "onedrive"),
                    "scan_timestamp": scan_result.get("scan_timestamp"),
                    "total_files": scan_result.get("total_items", 0),
                    "folders_found": len(scan_result.get("folders", [])),
                    "message": scan_result.get("message", "Data extracted from OneDrive files")
                }
                
                # Add folder information if available
                if scan_result.get("folders"):
                    dashboard_data["folder_summary"] = {
                        "rrf_folder": any("rrf" in f["name"].lower() for f in scan_result["folders"]),
                        "bench_folder": any("bench" in f["name"].lower() for f in scan_result["folders"]),
                        "certification_folder": any("certification" in f["name"].lower() for f in scan_result["folders"]),
                        "allocation_folder": any("allocation" in f["name"].lower() for f in scan_result["folders"]),
                        "utilization_folder": any("utilization" in f["name"].lower() for f in scan_result["folders"]),
                        "account_folder": any("account" in f["name"].lower() for f in scan_result["folders"])
                    }
                
                self.wfile.write(json.dumps(dashboard_data).encode())
            else:
                raise Exception("File scanner not available")
        except Exception as e:
            # Fallback to zero data if OneDrive is not available
            fallback_data = {
                "active_rrfs": 0,
                "bench_resources": 0,
                "active_projects": 0,
                "trainees": 0,
                "recent_rrf_updates": [],
                "training_progress": [],
                "data_source": "fallback",
                "message": f"OneDrive connection failed: {str(e)}"
            }
            self.wfile.write(json.dumps(fallback_data).encode())
    
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
