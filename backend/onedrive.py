import requests
from fastapi import HTTPException
from typing import List
import os

# Microsoft Graph API integration for OneDrive and SharePoint
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

class OneDriveClient:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def list_files(self, folder_path: str) -> List[dict]:
        """List files from OneDrive or SharePoint"""
        # Check if it's a SharePoint path
        if "sharepoint.com" in folder_path or "sites/" in folder_path:
            return self._list_sharepoint_files(folder_path)
        else:
            return self._list_onedrive_files(folder_path)

    def _list_onedrive_files(self, folder_path: str) -> List[dict]:
        """List files from OneDrive"""
        url = f"{GRAPH_API_BASE}/me/drive/root:/{folder_path}:/children"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to fetch files from OneDrive: {response.text}")
        return response.json().get('value', [])

    def _list_sharepoint_files(self, site_path: str) -> List[dict]:
        """List files from SharePoint site"""
        # Check if it's a site ID format (contains commas)
        if "," in site_path:
            # If it's just the site ID, access the root drive
            if "/" not in site_path:
                site_id = site_path
                # Use SharePoint API with site ID to access root drive
                url = f"{GRAPH_API_BASE}/sites/{site_id}/drive/root/children"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"Failed to fetch files from SharePoint: {response.text}")
                
                return response.json().get('value', [])
            else:
                # Format: SITE_ID/Shared Documents/PATH
                parts = site_path.split("/")
                if len(parts) >= 2:
                    site_id = parts[0]  # Full site ID
                    # Build the SharePoint path
                    sharepoint_path = "/".join(parts[1:]) if len(parts) > 1 else ""
                    
                    # Use SharePoint API with site ID
                    url = f"{GRAPH_API_BASE}/sites/{site_id}/drive/root:/{sharepoint_path}:/children"
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code != 200:
                        raise HTTPException(status_code=500, detail=f"Failed to fetch files from SharePoint: {response.text}")
                    
                    return response.json().get('value', [])
        
        # Check if it's a sites/ format
        elif "sites/" in site_path:
            # Format: sites/SITE_NAME/Shared Documents/PATH
            parts = site_path.split("/")
            if len(parts) >= 2:
                site_name = parts[1]  # GEICO-Managers
                # Build the SharePoint path
                sharepoint_path = "/".join(parts[2:]) if len(parts) > 2 else ""
                
                # Use SharePoint API
                url = f"{GRAPH_API_BASE}/sites/{site_name}:/drive/root:/{sharepoint_path}:/children"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    # Try alternative SharePoint API format
                    url = f"{GRAPH_API_BASE}/sites/{site_name}/drive/root:/{sharepoint_path}:/children"
                    response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"Failed to fetch files from SharePoint: {response.text}")
                
                return response.json().get('value', [])
        
        raise HTTPException(status_code=400, detail="Invalid SharePoint path format")

    def get_sharepoint_site_info(self, site_name: str) -> dict:
        """Get information about a SharePoint site"""
        url = f"{GRAPH_API_BASE}/sites/{site_name}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to get SharePoint site info: {response.text}")
        
        return response.json()

    def download_file(self, file_id: str, dest_path: str):
        url = f"{GRAPH_API_BASE}/me/drive/items/{file_id}/content"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to download file from OneDrive")
        with open(dest_path, "wb") as f:
            f.write(response.content)
