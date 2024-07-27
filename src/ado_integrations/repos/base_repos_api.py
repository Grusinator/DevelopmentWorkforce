from abc import ABC, abstractmethod
from typing import List

from src.ado_integrations.repos.ado_repos_models import AdoPullRequest, CreatePullRequestInput


class BaseAdoReposApi(ABC):
    @abstractmethod
    def create_pull_request(self, pr_input: "CreatePullRequestInput") -> int:
        pass

    @abstractmethod
    def get_pull_request(self, pr_id: int) -> "AdoPullRequest":
        pass

    @abstractmethod
    def update_pull_request_description(self, pr_id: int, description: str) -> int:
        pass

    @abstractmethod
    def list_pull_requests(self, repository_id: str, status: str = None) -> List["AdoPullRequest"]:
        pass

    @abstractmethod
    def approve_pull_request(self, pr_id: int) -> None:
        pass

    @abstractmethod
    def abandon_pull_request(self, pr_id: int) -> None:
        pass

    @abstractmethod
    def create_branch(self, repository_id: str, branch_name: str, source_branch: str) -> None:
        pass
