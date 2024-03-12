import base64

import requests
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import os
from dotenv import load_dotenv

load_dotenv()

class ADOConnection:
    def __init__(self):
        self.organization_url = os.getenv("ADO_ORGANIZATION_URL")
        self.personal_access_token = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
        self.project_name = os.getenv("ADO_PROJECT_NAME")  
        credentials = BasicAuthentication('', self.personal_access_token)  # Username is empty for PAT
        self.connection = Connection(base_url=self.organization_url, creds=credentials)
        print("Connected to ADO successfully!")

    def get_headers(self, method_type="GET"):
        encoded_bytes = base64.b64encode(f':{self.personal_access_token}'.encode('ascii'))
        encoded_pat = str(encoded_bytes, 'ascii')
        return {
            'Authorization': f'Basic {encoded_pat}',
            'Content-Type': 'application/json-patch+json' if method_type == "PATCH" else 'application/json',
        }

    def make_request(self, method, url, **kwargs):
        headers = self.get_headers(method)
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()


