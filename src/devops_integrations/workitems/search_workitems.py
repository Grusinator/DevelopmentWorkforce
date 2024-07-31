import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Environment variables
organization = "GrusinatorsAiCorp"
project = os.getenv("ADO_PROJECT_NAME")
personal_access_token = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")


class AzureDevOpsWorkItemSearch:
    def __init__(self, organization, project, personal_access_token):
        self.organization = organization
        self.project = project
        self.personal_access_token = personal_access_token
        self.base_url = f"https://almsearch.dev.azure.com/{organization}/{project}/_apis/search/workitemsearchresults?api-version=7.1-preview.1"
        self.headers = {
            'Content-Type': 'application/json'
        }

    def fetch_work_items(self, search_text, top=10, skip=0):
        payload = {
            "searchText": search_text,
            "$top": top,
            "$skip": skip,
            "filters": None,
            "includeFacets": False
        }

        response = requests.post(
            self.base_url,
            auth=HTTPBasicAuth('', self.personal_access_token),
            headers=self.headers,
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


if __name__ == "__main__":
    azure_devops_search = AzureDevOpsWorkItemSearch(organization, project, personal_access_token)
    try:
        search_text = "snake"  # Change this to your desired search text
        results = azure_devops_search.fetch_work_items(search_text)
        print(results)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
