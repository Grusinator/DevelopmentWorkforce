import os
import time
from typing import List

from azure.devops.connection import Connection
from azure.devops.v7_1.git import GitPullRequestCompletionOptions, GitPullRequest, GitRefUpdate, \
    GitPullRequestSearchCriteria
from msrest.authentication import BasicAuthentication

from development_workforce.ado_integrations.repos.base_repos_api import BaseAdoReposApi
from development_workforce.ado_integrations.repos.ado_repos_models import CreatePullRequestInput, AdoPullRequest


class ADOReposWrapperApi(BaseAdoReposApi):
    def __init__(self):
        self.organization_url = os.getenv("ADO_ORGANIZATION_URL")
        self.personal_access_token = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
        self.project_name = os.getenv("ADO_PROJECT_NAME")
        self.repo_name = os.getenv("ADO_REPO_NAME")
        credentials = BasicAuthentication('', self.personal_access_token)
        self.connection = Connection(base_url=self.organization_url, creds=credentials)
        self.client = self.connection.clients.get_git_client()

    def create_pull_request(self, pr_input: CreatePullRequestInput) -> int:
        repository_id = self.get_repository_id()
        pr = GitPullRequest(
            source_ref_name=f"refs/heads/{pr_input.source_branch}",
            target_ref_name=f"refs/heads/{pr_input.target_branch}",
            title=pr_input.title,
            description=pr_input.description
        )
        created_pr = self.client.create_pull_request(pr, repository_id, self.project_name)
        return created_pr.pull_request_id

    def get_pull_request(self, pr_id: int) -> AdoPullRequest:
        repository_id = self.get_repository_id()
        pr = self.client.get_pull_request(repository_id, pr_id)
        return AdoPullRequest(
            id=pr.pull_request_id,
            title=pr.title,
            description=pr.description,
            source_branch=pr.source_ref_name,
            target_branch=pr.target_ref_name,
            status=pr.status
        )

    def update_pull_request_description(self, pr_id: int, description: str) -> int:
        repository_id = self.get_repository_id()
        pr = self.client.get_pull_request(repository_id, pr_id)
        pr.description = description
        updated_pr = self.client.update_pull_request(pr, repository_id, pr_id)
        return updated_pr.pull_request_id

    def list_pull_requests(self, repository_id: str, status: str = None) -> List[AdoPullRequest]:
        search_criteria = GitPullRequestSearchCriteria(status=status)
        prs = self.client.get_pull_requests(repository_id, search_criteria, project=self.project_name)
        return [AdoPullRequest(
            id=pr.pull_request_id,
            title=pr.title,
            description=pr.description,
            source_branch=pr.source_ref_name,
            target_branch=pr.target_ref_name,
            status=pr.status
        ) for pr in prs]

    def complete_pull_request(self, pr_id: int) -> None:
        repository_id = self.get_repository_id()
        pr = self.client.get_pull_request(repository_id, pr_id, project=self.project_name)
        completion_options = GitPullRequestCompletionOptions(delete_source_branch=False)
        pr.status = "completed"  # Assuming 'completed' is a valid status; adjust as necessary
        self.client.update_pull_request(pr, repository_id, pr_id, project=self.project_name,
                                        completion_options=completion_options)

    def abandon_pull_request(self, pr_id: int) -> None:
        repository_id = self.get_repository_id()
        pr = self.client.get_pull_request(repository_id, pr_id)
        pr.status = 'abandoned'
        self.client.update_pull_request(pr, repository_id, pr_id)

    def create_branch(self, repository_id: str, branch_name: str, source_branch: str) -> None:
        refs = self.client.get_refs(repository_id, filter=f"heads/{source_branch}")
        if not refs:
            raise ValueError(f"Source branch '{source_branch}' not found.")
        source_ref = refs[0]
        new_ref = GitRefUpdate(
            name=f"refs/heads/{branch_name}",
            old_object_id="0000000000000000000000000000000000000000",
            new_object_id=source_ref.object_id
        )
        self.client.update_refs(ref_updates=[new_ref], repository_id=repository_id, project=self.project_name)


    def branch_exists(self, repository_id: str, branch_name: str) -> bool:
        refs = self.client.get_refs(repository_id, filter=f"heads/{branch_name}")
        return len(refs) > 0

    def get_repository_id(self) -> str:
        # Assuming a single repository for simplicity. Adapt as necessary.
        repositories = self.client.get_repositories(self.project_name)
        repo = [repo for repo in repositories if repo.name == self.repo_name][0]
        return repo.id if repositories else None
