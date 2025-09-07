from http.server import BaseHTTPRequestHandler
import json

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
            
            # Simple AI-like responses based on keywords
            question_lower = question.lower()
            
            if any(word in question_lower for word in ['rrf', 'active', 'ticket']):
                answer = "Currently there are 24 active RRFs in the system. The most recent ones include Senior Developer positions at TechCorp, Project Manager at FinanceInc, and Data Analyst at RetailCo. Would you like me to show you more details about any specific RRF?"
            elif any(word in question_lower for word in ['training', 'course', 'learn']):
                answer = "We have several training programs in progress: Agile Methodology (15 trainees, 75% complete), Cloud Computing (8 trainees, 100% complete), and Data Science (12 trainees, 60% complete). Which training program would you like to know more about?"
            elif any(word in question_lower for word in ['bench', 'resource', 'available']):
                answer = "There are currently 3 bench resources available. The system uptime is 99.9% and compliance is at 92% across all policies. Would you like me to provide more specific details about bench resources?"
            elif any(word in question_lower for word in ['help', 'assist', 'support']):
                answer = "I'm here to help with operations, RRFs, training, and resource management. You can ask me about active tickets, training progress, bench resources, or any other operations-related questions. What would you like to know?"
            else:
                answer = f"I understand you're asking about '{question}'. As your Operations AI assistant, I can help with RRFs, training programs, bench resources, and system status. Could you be more specific about what information you need?"
            
            response = {
                "answer": answer,
                "confidence": 0.9,
                "sources": ["Operations Database", "Training Records", "Resource Management System"]
            }
            
            self.send_success_response(response)
            
        except Exception as e:
            self.send_error_response(500, f"Bot query failed: {str(e)}")
    
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
