import os
import requests
from typing import Optional

class NangoService:
    def __init__(self, secret_key: Optional[str] = None, base_url: str = "https://api.nango.dev"):
        self.secret_key = secret_key or os.getenv("NANGO_SECRET_KEY")
        self.base_url = base_url
        print(f"DEBUG: NANGO_SECRET_KEY present: {bool(self.secret_key)}")
        if not self.secret_key:
            print(f"DEBUG: Current CWD: {os.getcwd()}")
            print(f"DEBUG: .env exists in CWD? {os.path.exists('.env')}")
            print(f"DEBUG: All Env Keys: {list(os.environ.keys())}")

    def get_connection_token(self, connection_id: str, provider_config_key: str) -> Optional[str]:
        """
        Fetch the access token for a given connection from Nango.
        
        Args:
            connection_id: The unique ID of the connection (e.g. user ID).
            provider_config_key: The integration key (e.g. 'google-drive').
            
        Returns:
            The access token string, or None if failed.
        """
        if not self.secret_key:
            print("Error: NANGO_SECRET_KEY not set.")
            return None

        url = f"{self.base_url}/connection/{connection_id}"
        headers = {
            "Authorization": f"Bearer {self.secret_key}"
        }
        params = {
            "provider_config_key": provider_config_key
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            # Depending on Nango API version, token location might vary.
            # Usually: credentials -> access_token
            return data.get("credentials", {}).get("access_token")
        except Exception as e:
            print(f"Failed to fetch Nango token: {e}")
            return None

    def create_connect_session(self, user_id: str) -> Optional[str]:
        """
        Create a new Connect Session Token for the frontend.
        """
        if not self.secret_key:
            return None
        
        # Correct Endpoint per docs
        url = f"{self.base_url}/connect/sessions"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        # Correct Body per docs
        data = { 
            "end_user": {
                "id": user_id
            },
            "allowed_integrations": ["google-drive"], # Optional: Whitelist specific integration
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            json_data = response.json()
            # Response: { "data": { "token": "...", ... } }
            return json_data.get("data", {}).get("token")
        except Exception as e:
            msg = f"Failed to create Nango session: {e}"
            if hasattr(e, 'response') and e.response is not None:
                msg += f" | Body: {e.response.text}"
            print(msg)
            raise Exception(msg)

nango_service = NangoService()
