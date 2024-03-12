import base64

from development_workforce.ado_integrations.ado_connection import ADOConnection


class AdoRepo(ADOConnection):

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
        url = f"{self.base_url}/pullrequests?api-version=7.1-preview.1"
        document = {
            "title": "My Pull Request",
            "description": "This is a pull request",
            "sourceRefName": f"refs/heads/{from_branch}",
            "targetRefName": F"refs/heads/{into_branch}",
            "reviewers": []
        }
        resp = self.make_request('POST', url, json=document)
        return resp['pullRequestId']
    
    def update_pull_request(self, pull_request_id, **kwargs):
        url = f"{self.base_url}/pullrequests/{pull_request_id}?api-version=7.1-preview.1"
        document = kwargs
        self.make_request('PATCH', url, json=document)

    def approve_pull_request(self, pull_request_id):
        self.update_pull_request(pull_request_id, status="approved")

    def reject_pull_request(self, pull_request_id):
        self.update_pull_request(pull_request_id, status="rejected")

    def abandon_pull_request(self, pull_request_id):
        self.update_pull_request(pull_request_id, status="abandoned")

    def merge_pull_request(self, pull_request_id):
        url = f"{self.base_url}/pullrequests/{pull_request_id}?api-version=7.1-preview.1"
        self.make_request('PATCH', url)

    def write_comment(self, pull_request_id, comment):
        url = f"{self.base_url}/pullrequests/{pull_request_id}/threads?api-version=7.1-preview.1"
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
        url = f"{self.base_url}/pullrequests?api-version=7.1-preview.1"
        return self.make_request('GET', url)
    


#     import requests
# import json

# class AdoRepo(ADOConnection):

#     def __init__(self, repo_name):
#         super().__init__()
#         self.repo_name = repo_name

#     def update_pull_request(self, pull_request_id, status=None, title=None, description=None):
#         url = f"{self.organization_url}/{self.project_name}/_apis/git/repositories/{self.repo_name}/pullrequests/{pull_request_id}?api-version=7.1-preview.1"
#         headers = {"Content-Type": "application/json"}
#         data = {}

#         if status is not None:
#             data["status"] = status
#         if title is not None:
#             data["title"] = title
#         if description is not None:
#             data["description"] = description

#         response = requests.patch(url, headers=headers, data=json.dumps(data), auth=('token', self.token))

#         if response.status_code != 200:
#             raise Exception(f"Failed to update pull request: {response.text}")

#         return response.json()

#     def approve_pull_request(self, pull_request_id):
#         return self.update_pull_request(pull_request_id, status="approved")

#     def reject_pull_request(self, pull_request_id):
#         return self.update_pull_request(pull_request_id, status="rejected")

#     def abandon_pull_request(self, pull_request_id):
#         return self.update_pull_request(pull_request_id, status="abandoned")