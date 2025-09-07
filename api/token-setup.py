#!/usr/bin/env python3
"""
Vercel API route for OneDrive token setup
"""

import json
import os
import re
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class TokenSetupHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests for token setup page"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        html_content = self._get_token_setup_html()
        self.wfile.write(html_content.encode())
    
    def do_POST(self):
        """Handle POST requests for token setup"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            action = data.get('action')
            
            if action == 'test_token':
                result = self._test_token(data.get('token', ''))
            elif action == 'setup_token':
                result = self._setup_token(data.get('token', ''))
            elif action == 'get_token_info':
                result = self._get_token_info()
            else:
                result = {"error": "Invalid action"}
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            error_response = {"error": f"Request processing failed: {str(e)}"}
            self.wfile.write(json.dumps(error_response).encode())
    
    def _test_token(self, token):
        """Test if a OneDrive token is valid"""
        if not token:
            return {"error": "No token provided"}
        
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Test with a simple Graph API call
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": f"Token is valid! Connected as: {user_data.get('displayName', 'Unknown')}",
                    "user_info": user_data
                }
            else:
                return {
                    "success": False,
                    "error": f"Token test failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Token test error: {str(e)}"
            }
    
    def _setup_token(self, token):
        """Set up the hardcoded token in the application"""
        if not token:
            return {"error": "No token provided"}
        
        try:
            # Test the token first
            test_result = self._test_token(token)
            if not test_result.get("success"):
                return test_result
            
            # In Vercel, we can't modify files, so we'll store the token in environment
            # and update the token manager to use it
            return {
                "success": True,
                "message": "Token validated successfully! In Vercel, you'll need to update the environment variable ONEDRIVE_ACCESS_TOKEN with this token.",
                "user_info": test_result.get("user_info"),
                "vercel_instructions": {
                    "step1": "Go to your Vercel dashboard",
                    "step2": "Select your project",
                    "step3": "Go to Settings → Environment Variables",
                    "step4": "Update ONEDRIVE_ACCESS_TOKEN with your token",
                    "step5": "Redeploy your application"
                }
            }
                
        except Exception as e:
            return {"error": f"Token setup failed: {str(e)}"}
    
    def _get_token_info(self):
        """Get information about the current token setup"""
        try:
            # Check environment variable
            env_token = os.getenv("ONEDRIVE_ACCESS_TOKEN", "")
            
            if env_token:
                return {
                    "token_set": True,
                    "token_preview": f"{env_token[:10]}...{env_token[-10:]}",
                    "message": "Token is configured via environment variable",
                    "source": "environment"
                }
            else:
                return {
                    "token_set": False,
                    "message": "No token configured in environment variables"
                }
                    
        except Exception as e:
            return {"error": f"Failed to get token info: {str(e)}"}
    
    def _get_token_setup_html(self):
        """Generate HTML for token setup page"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OneDrive Token Setup - Ops Bot</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .step {
            margin: 20px 0;
            padding: 20px;
            border-left: 4px solid #007acc;
            background-color: #f8f9fa;
        }
        .step h3 {
            margin-top: 0;
            color: #007acc;
        }
        .token-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            margin: 10px 0;
        }
        .btn {
            background-color: #007acc;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
        }
        .btn:hover {
            background-color: #005a9e;
        }
        .btn:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .status {
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .status.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .link {
            color: #007acc;
            text-decoration: none;
        }
        .link:hover {
            text-decoration: underline;
        }
        .token-preview {
            font-family: monospace;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            margin: 10px 0;
        }
        .vercel-instructions {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .vercel-instructions h4 {
            margin-top: 0;
            color: #856404;
        }
        .vercel-instructions ol {
            margin: 10px 0;
            padding-left: 20px;
        }
        .vercel-instructions li {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 OneDrive Token Setup</h1>
        
        <div id="status"></div>
        
        <div class="step">
            <h3>Step 1: Get Your OneDrive Token</h3>
            <p>1. Go to <a href="https://developer.microsoft.com/en-us/graph/graph-explorer" target="_blank" class="link">Microsoft Graph Explorer</a></p>
            <p>2. Sign in with your Microsoft account</p>
            <p>3. In the 'Modify permissions' tab, add these permissions:</p>
            <ul>
                <li><code>Files.ReadWrite.All</code></li>
                <li><code>Sites.ReadWrite.All</code></li>
                <li><code>User.Read</code></li>
            </ul>
            <p>4. Click 'Generate Token'</p>
            <p>5. Copy the access token</p>
        </div>
        
        <div class="step">
            <h3>Step 2: Test Your Token</h3>
            <input type="text" id="tokenInput" class="token-input" placeholder="Paste your access token here...">
            <br>
            <button onclick="testToken()" class="btn">Test Token</button>
            <button onclick="setupToken()" class="btn" id="setupBtn" disabled>Get Vercel Instructions</button>
        </div>
        
        <div class="step">
            <h3>Step 3: Check Current Status</h3>
            <button onclick="checkTokenStatus()" class="btn">Check Status</button>
            <div id="tokenStatus"></div>
        </div>
        
        <div class="step">
            <h3>Next Steps</h3>
            <p>Once your token is set up:</p>
            <ul>
                <li>✅ Your Ops Bot will connect to OneDrive automatically</li>
                <li>✅ Dashboard will show real data from your files</li>
                <li>✅ QA bot will answer questions based on your actual data</li>
                <li>✅ No more token management needed!</li>
            </ul>
        </div>
    </div>

    <script>
        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
        }
        
        function showTokenStatus(message, type = 'info') {
            const statusDiv = document.getElementById('tokenStatus');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
        }
        
        async function testToken() {
            const token = document.getElementById('tokenInput').value.trim();
            if (!token) {
                showStatus('Please enter a token first', 'error');
                return;
            }
            
            showStatus('Testing token...', 'info');
            
            try {
                const response = await fetch('/api/token-setup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'test_token',
                        token: token
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus(result.message, 'success');
                    document.getElementById('setupBtn').disabled = false;
                } else {
                    showStatus(result.error, 'error');
                    document.getElementById('setupBtn').disabled = true;
                }
            } catch (error) {
                showStatus('Error testing token: ' + error.message, 'error');
            }
        }
        
        async function setupToken() {
            const token = document.getElementById('tokenInput').value.trim();
            if (!token) {
                showStatus('Please enter a token first', 'error');
                return;
            }
            
            showStatus('Getting Vercel setup instructions...', 'info');
            
            try {
                const response = await fetch('/api/token-setup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'setup_token',
                        token: token
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    let message = result.message;
                    if (result.vercel_instructions) {
                        message += '<div class="vercel-instructions"><h4>Vercel Setup Instructions:</h4><ol>';
                        Object.values(result.vercel_instructions).forEach(step => {
                            message += `<li>${step}</li>`;
                        });
                        message += '</ol></div>';
                    }
                    showStatus(message, 'success');
                } else {
                    showStatus(result.error, 'error');
                }
            } catch (error) {
                showStatus('Error getting instructions: ' + error.message, 'error');
            }
        }
        
        async function checkTokenStatus() {
            showTokenStatus('Checking status...', 'info');
            
            try {
                const response = await fetch('/api/token-setup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'get_token_info'
                    })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showTokenStatus(result.error, 'error');
                } else if (result.token_set) {
                    showTokenStatus(`✅ Token is configured: <div class="token-preview">${result.token_preview}</div><br>Source: ${result.source}`, 'success');
                } else {
                    showTokenStatus('❌ No token configured', 'error');
                }
            } catch (error) {
                showTokenStatus('Error checking status: ' + error.message, 'error');
            }
        }
        
        // Check status on page load
        window.onload = function() {
            checkTokenStatus();
        };
    </script>
</body>
</html>
        """

def handler(request):
    """Vercel serverless function handler"""
    return TokenSetupHandler()
