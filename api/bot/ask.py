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
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            question = data.get('question', '')
            
            if not question.strip():
                self.send_error_response(400, "Question is required")
                return
            
            # Get real data from OneDrive to provide accurate responses
            if file_scanner:
                scan_result = file_scanner.scan_all_folders()
                real_data = scan_result["extracted_data"]
                real_data["total_files"] = scan_result.get("total_items", 0)
                real_data["data_source"] = scan_result.get("data_source", "onedrive")
            else:
                real_data = self._get_fallback_data()
            
            # Generate response based on real data
            answer = self._generate_response(question, real_data)
            
            response = {
                "answer": answer,
                "confidence": 0.9,
                "sources": ["OneDrive Operations Data", "SharePoint Files", "Real-time Data"]
            }
            
            self.send_success_response(response)
            
        except Exception as e:
            self.send_error_response(500, f"Bot query failed: {str(e)}")
    
    
    def _get_fallback_data(self):
        """Return fallback data when OneDrive is not available"""
        return {
            "active_rrfs": 0,
            "bench_resources": 0,
            "active_projects": 0,
            "trainees": 0,
            "file_count": 0,
            "file_names": [],
            "data_source": "fallback"
        }
    
    def _generate_response(self, question, data):
        """Generate response based on real data"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['rrf', 'active', 'request']):
            if data["active_rrfs"] > 0:
                return f"Based on the files in OneDrive, I found {data['active_rrfs']} RRF-related files. The system is currently processing these files to extract detailed information. Would you like me to provide more specific details about any particular RRF?"
            else:
                return "I don't see any RRF files in the OneDrive folder currently. Please ensure RRF files are uploaded to the Operations folder."
        
        elif any(word in question_lower for word in ['training', 'course', 'learn']):
            if data["trainees"] > 0:
                return f"I found {data['trainees']} training-related files in OneDrive. The system is processing these files to extract training program details. Would you like me to provide more information about specific training programs?"
            else:
                return "I don't see any training files in the OneDrive folder currently. Please ensure training files are uploaded to the Operations folder."
        
        elif any(word in question_lower for word in ['bench', 'resource', 'available']):
            if data["bench_resources"] > 0:
                return f"I found {data['bench_resources']} bench resource files in OneDrive. The system is processing these files to extract resource availability information. Would you like me to provide more details about bench resources?"
            else:
                return "I don't see any bench resource files in the OneDrive folder currently. Please ensure resource files are uploaded to the Operations folder."
        
        elif any(word in question_lower for word in ['project']):
            if data["active_projects"] > 0:
                return f"I found {data['active_projects']} project-related files in OneDrive. The system is processing these files to extract project information. Would you like me to provide more details about active projects?"
            else:
                return "I don't see any project files in the OneDrive folder currently. Please ensure project files are uploaded to the Operations folder."
        
        elif any(word in question_lower for word in ['help', 'assist', 'support']):
            return f"I'm here to help with operations data analysis. I can see {data['file_count']} files in the OneDrive folder. I can help you with RRFs, training programs, bench resources, and project information. What would you like to know more about?"
        
        else:
            return f"I understand you're asking about '{question}'. I can see {data['file_count']} files in the OneDrive folder. As your Operations AI assistant, I can help analyze RRFs, training programs, bench resources, and project data. Could you be more specific about what information you need?"
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        error_response = {"detail": message}
        self.wfile.write(json.dumps(error_response).encode())
