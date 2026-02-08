import requests
import os

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000/api"):
        self.base_url = base_url
        self.token = None 
        # In a real app, load token from file/secure storage
    
    def set_token(self, token):
        self.token = token
    
    def _get_headers(self):
        headers = {}
        if self.token:
            headers['Authorization'] = f'Token {self.token}'
        return headers

    def login(self, username, password):
        try:
            response = requests.post(f"{self.base_url}/login/", json={'username': username, 'password': password})
            response.raise_for_status()
            data = response.json()
            self.token = data.get('token')
            return True, "Login successful"
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def register(self, username, email, password):
        try:
            response = requests.post(f"{self.base_url}/register/", json={'username': username, 'email': email, 'password': password})
            response.raise_for_status()
            return True, "Registration successful"
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def upload_file(self, file_path):
        if not self.token:
            return False, "Not authenticated"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.base_url}/upload/", files=files, headers=self._get_headers())
                response.raise_for_status()
                return True, response.json()
        except Exception as e:
            return False, str(e)

    def get_summary(self):
        if not self.token:
            return None
        try:
            response = requests.get(f"{self.base_url}/summary/", headers=self._get_headers())
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def get_history(self):
        if not self.token:
            return []
        try:
            response = requests.get(f"{self.base_url}/history/", headers=self._get_headers())
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def download_report(self, dataset_id, save_path):
        if not self.token:
            return False, "Not authenticated"
        try:
            response = requests.get(f"{self.base_url}/report/{dataset_id}/", headers=self._get_headers(), stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True, "Download successful"
        except Exception as e:
            return False, str(e)

# Singleton instance
client = APIClient()
