import base64

from src.ado_integrations.ado_connection import ADOConnection


class AdoRepo(ADOConnection):
    api_version = "7.1-preview.1"  # Class variable for API version

    def __init__(self, repo_name):
        super().__init__()
        self.repo_name = repo_name
        self.base_url = f"{self.organization_url}/{self.project_name}/_apis/git/repositories/{self.repo_name}"

    def get_headers(self, method_type="GET"):
        encoded_bytes = base64.b64encode(f':{self.personal_access_token}'.encode('ascii'))
        encoded_pat = str(encoded_bytes, 'ascii')
        return {
            'Authorization': f'Basic {encoded_pat}',
            'Content-Type': 'application/json',
        }

    def create_pull_request(self, from_branch, into_branch="main") -> int:
        url = f"{self.base_url}/pullrequests?api-version={self.api_version}"
        document = {
            "title": "My Pull Request",
            "description": "This is a pull request",
            "sourceRefName": f"refs/heads/{from_branch}",
            "targetRefName": f"refs/heads/{into_branch}",
            "reviewers": []
        }
        resp = self.make_request('POST', url, json=document)
        return resp['pullRequestId']

    def update_pull_request(self, pull_request_id, **kwargs):
        url = f"{self.base_url}/pullrequests/{pull_request_id}?api-version={self.api_version}"
        document = kwargs
        self.make_request('PATCH', url, json=document)

    def approve_pull_request(self, pull_request_id):
        self.update_pull_request(pull_request_id, status="completed")

    def reject_pull_request(self, pull_request_id):
        self.update_pull_request(pull_request_id, status="rejected")

    def abandon_pull_request(self, pull_request_id):
        self.update_pull_request(pull_request_id, status="abandoned")

    def merge_pull_request(self, pull_request_id):
        url = f"{self.base_url}/pullrequests/{pull_request_id}?api-version={self.api_version}"
        self.make_request('PATCH', url)

    def write_comment(self, pull_request_id, comment):
        url = f"{self.base_url}/pullrequests/{pull_request_id}/threads?api-version={self.api_version}"
        document = {
            "comments": [
                {
                    "parentCommentId": 0,
                    "content": comment
                }
            ]
        }
        self.make_request('POST', url, json=document)

    def list_pull_requests(self):
        url = f"{self.base_url}/pullrequests?api-version={self.api_version}"
        return self.make_request('GET', url)
