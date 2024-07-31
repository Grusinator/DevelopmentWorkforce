import base64

import requests
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from src.devops_integrations.models import ProjectAuthenticationModel


class ADOConnection:
    def __init__(self, auth: ProjectAuthenticationModel):
        self.auth = auth
        self.organization_url = f"https://dev.azure.com/{auth.ado_org_name}"
        credentials = BasicAuthentication('', auth.pat)
        self.connection = Connection(base_url=self.organization_url, creds=credentials)
        self.client = self.connection.clients.get_git_client()
        self.build_client = self.connection.clients.get_build_client()
        self.core_client = self.connection.clients.get_core_client()
        self.wo_client = self.connection.clients.get_work_item_tracking_client()

    def get_headers(self, method_type="GET"):
        encoded_bytes = base64.b64encode(f':{self.auth.pat}'.encode('ascii'))
        encoded_pat = str(encoded_bytes, 'ascii')
        return {
            'Authorization': f'Basic {encoded_pat}',
            'Content-Type': 'application/json',
        }

    def make_request(self, method, url, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = self.get_headers(method)
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
