"""
Token Manager for OneDrive/SharePoint authentication
Handles token refresh and validation
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class TokenManager:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.client_id = os.getenv("ONEDRIVE_CLIENT_ID", "")
        self.client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET", "")
        self.tenant_id = os.getenv("ONEDRIVE_TENANT_ID", "13085c86-4bcb-460a-a6f0-b373421c6323")
        
    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary"""
        if self.access_token and self._is_token_valid():
            return self.access_token
        
        # Try to refresh the token
        if self._refresh_token():
            return self.access_token
        
        return None
    
    def _is_token_valid(self) -> bool:
        """Check if the current token is still valid"""
        if not self.token_expires_at:
            return False
        
        # Add 5 minute buffer to avoid edge cases
        buffer_time = datetime.now() + timedelta(minutes=5)
        return self.token_expires_at > buffer_time
    
    def _refresh_token(self) -> bool:
        """Refresh the access token using refresh token"""
        try:
            # For now, we'll use the manual token approach
            # In production, you'd implement proper OAuth2 flow
            return self._get_manual_token()
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return False
    
    def _get_manual_token(self) -> bool:
        """Get token from environment variable (Vercel compatible)"""
        # For Vercel deployment, use environment variable
        manual_token = os.getenv("ONEDRIVE_ACCESS_TOKEN", "")
        
        if manual_token:
            self.access_token = manual_token
            # Set expiration to 1 hour from now (typical token lifetime)
            self.token_expires_at = datetime.now() + timedelta(hours=1)
            return True
        
        # Fallback to hardcoded token for local development
        hardcoded_token = "YOUR_ONEDRIVE_ACCESS_TOKEN_HERE"
        if hardcoded_token != "YOUR_ONEDRIVE_ACCESS_TOKEN_HERE":
            self.access_token = hardcoded_token
            self.token_expires_at = datetime.now() + timedelta(hours=1)
            return True
            
        return False
    
    def refresh_token_from_env(self) -> bool:
        """Refresh token from hardcoded source"""
        # With hardcoded token, this just reloads the same token
        return self._get_manual_token()
    
    def get_token_info(self) -> dict:
        """Get information about the current token"""
        return {
            "has_token": bool(self.access_token),
            "token_length": len(self.access_token) if self.access_token else 0,
            "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "is_expired": self.is_token_expired() if self.token_expires_at else True,
            "source": "hardcoded" if self.access_token and self.access_token != "YOUR_ONEDRIVE_ACCESS_TOKEN_HERE" else "environment"
        }
    
    def validate_token(self, token: str) -> bool:
        """Validate if a token is working by making a test API call"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_token_info(self) -> Dict[str, Any]:
        """Get information about the current token"""
        return {
            "has_token": bool(self.access_token),
            "is_valid": self._is_token_valid() if self.access_token else False,
            "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "time_until_expiry": str(self.token_expires_at - datetime.now()) if self.token_expires_at else None
        }

# Global token manager instance
token_manager = TokenManager()
