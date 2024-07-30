from typing import List
from src.ado_integrations.repos.ado_repos_models import AdoPullRequest, CreatePullRequestInput
from src.ado_integrations.repos.base_repos_api import BaseAdoReposApi


class MockRepoApi(BaseAdoReposApi):
    def create_pull_request(self, pr_input: CreatePullRequestInput) -> int:
        return 1  # Mocked PR ID

    def get_pull_request(self, pr_id: int) -> AdoPullRequest:
        return AdoPullRequest(
            id=pr_id,
            title="Mock PR",
            description="This is a mock pull request",
            source_branch="feature-branch",
            target_branch="main",
            status="active"
        )

    def update_pull_request_description(self, pr_id: int, description: str) -> int:
        return pr_id  # Mocked return of the same PR ID

    def list_pull_requests(self, repository_id: str, status: str = None) -> List[AdoPullRequest]:
        return [
            AdoPullRequest(
                id=1,
                title="Mock PR 1",
                description="This is the first mock pull request",
                source_branch="feature-branch-1",
                target_branch="main",
                status="active"
            ),
            AdoPullRequest(
                id=2,
                title="Mock PR 2",
                description="This is the second mock pull request",
                source_branch="feature-branch-2",
                target_branch="main",
                status="completed"
            )
        ]

    def approve_pull_request(self, pr_id: int) -> None:
        pass  # Mocked method does nothing

    def abandon_pull_request(self, pr_id: int) -> None:
        pass  # Mocked method does nothing

    def create_branch(self, repository_id: str, branch_name: str, source_branch: str) -> None:
        pass  # Mocked method does nothing
