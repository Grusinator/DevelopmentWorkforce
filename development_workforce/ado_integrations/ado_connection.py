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


