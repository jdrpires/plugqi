import os
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import json
from dotenv import load_dotenv

load_dotenv()

class QiTechClient:
    def __init__(self):
        self.client_key = os.getenv('QITECH_CLIENT_KEY')
        self.private_key_path = os.getenv('QITECH_PRIVATE_KEY_PATH')
        self.base_url = os.getenv('QITECH_BASE_URL', 'https://api-auth.qitech.app')
        self.private_key = self._load_private_key()
    
    def _load_private_key(self):
        with open(self.private_key_path, 'rb') as key_file:
            return serialization.load_pem_private_key(key_file.read(), password=None)
    
    def _sign_request(self, method, endpoint, body=None):
        message = f"{method}|{endpoint}|{body or ''}"
        signature = self.private_key.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def _make_request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        body = json.dumps(data) if data else None
        signature = self._sign_request(method, endpoint, body)
        
        headers = {
            'Authorization': f'QI {self.client_key}:{signature}',
            'Content-Type': 'application/json'
        }
        
        response = requests.request(method, url, headers=headers, data=body)
        return response.json() if response.content else {}
