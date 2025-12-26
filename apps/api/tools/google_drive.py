from pydantic_ai import RunContext
from dataclasses import dataclass
import requests
import json
from typing import Optional, Any

@dataclass
class DriveDeps:
    access_token: str

def export_to_drive(ctx: RunContext[Any], filename: str, content: str, folder_id: Optional[str] = None) -> str:
    """
    Export text content to a file in Google Drive.
    
    Args:
        ctx: Dependency context containing the Google Drive access token (must have .access_token).
        filename: Name of the file to create (e.g., 'summary.txt', 'extraction.json').
        content: The text content to write to the file.
        folder_id: Optional ID of the parent folder.
        
    Returns:
        A success message with the link to the file, or an error message.
    """
    if hasattr(ctx.deps, 'access_token'):
        token = ctx.deps.access_token
    else:
        return "Error: Context missing access token."

    if not token:
        return "Error: No valid access token provided for Google Drive."

    metadata = {
        "name": filename,
        "mimeType": "text/plain"  # Defaulting to text/plain for simplicity
    }
    
    # Auto-detect JSON
    if filename.endswith(".json"):
        metadata["mimeType"] = "application/json"
    elif filename.endswith(".md"):
         metadata["mimeType"] = "text/markdown" # Drive converts this or keeps as text

    if folder_id:
        metadata["parents"] = [folder_id]

    # Multiplayer upload (metadata + media) is cleaner via client lib, 
    # but raw HTTP is fine for simple text.
    
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    headers = {"Authorization": f"Bearer {token}"}
    
    files = {
        'metadata': ('metadata', json.dumps(metadata), 'application/json'),
        'file': ('file', content, metadata["mimeType"])
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            res_json = response.json()
            file_id = res_json.get("id")
            # Get the webViewLink for the user
            # Need a second call or field expansion? 
            # create response usually returns id, name, mimeType.
            # Let's just return the ID and construct a link? Or fetch fields.
            
            # Fetch generic file fields to get the link
            fields_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=webViewLink,name"
            fields_resp = requests.get(fields_url, headers=headers)
            if fields_resp.status_code == 200:
                link = fields_resp.json().get("webViewLink", "")
                return f"Successfully uploaded '{filename}' to Google Drive. Link: {link}"
            
            return f"Successfully uploaded '{filename}' (ID: {file_id})."
        else:
            return f"Failed to upload to Google Drive. Status: {response.status_code}, Error: {response.text}"
            
    except Exception as e:
        return f"Exception during upload: {str(e)}"
