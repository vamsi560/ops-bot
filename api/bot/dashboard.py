from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = {
            "active_rrfs": 24,
            "bench_resources": 3,
            "active_projects": 99.9,
            "trainees": 92,
            "recent_rrf_updates": [
                {
                    "role": "Senior Developer",
                    "client": "TechCorp",
                    "status": "Active",
                    "date": "2024-01-15"
                },
                {
                    "role": "Project Manager",
                    "client": "FinanceInc",
                    "status": "Pending",
                    "date": "2024-01-14"
                },
                {
                    "role": "Data Analyst",
                    "client": "RetailCo",
                    "status": "Active",
                    "date": "2024-01-13"
                }
            ],
            "training_progress": [
                {
                    "title": "Agile Methodology",
                    "trainees": 15,
                    "status": "In Progress",
                    "progress": "75%"
                },
                {
                    "title": "Cloud Computing",
                    "trainees": 8,
                    "status": "Completed",
                    "progress": "100%"
                },
                {
                    "title": "Data Science",
                    "trainees": 12,
                    "status": "In Progress",
                    "progress": "60%"
                }
            ]
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
