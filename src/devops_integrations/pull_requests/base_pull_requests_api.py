from abc import ABC, abstractmethod
from typing import List
from src.devops_integrations.pull_requests.pull_request_models import CreatePullRequestInput, PullRequest, \
    PullRequestComment, PullRequestCommentThread


class BasePullRequestsApi(ABC):
    @abstractmethod
    def create_pull_request(self, repository_id: str, pr_input: CreatePullRequestInput) -> int:
        pass

    @abstractmethod
    def get_pull_request(self, repository_id: str, pr_id: int) -> PullRequest:
        pass

    @abstractmethod
    def list_pull_requests(self, repository_id: str, status: str = None, created_by=None) -> List[PullRequest]:
        pass

    @abstractmethod
    def approve_pull_request(self, repo_name: str, pr_id: int) -> None:
        pass

    @abstractmethod
    def abandon_pull_request(self, repo_name: str, pr_id: int) -> None:
        pass

    @abstractmethod
    def add_pull_request_comment(self, repo_name: str, pr_id: int, content: str) -> int:
        pass

    @abstractmethod
    def get_pull_request_comments(self, repo_name: str, pull_request_id: int) -> List[PullRequestCommentThread]:
        pass

    @abstractmethod
    def run_build(self, pr_id: int) -> int:
        pass

    @abstractmethod
    def get_build_status(self, pr_id: int) -> str:
        pass

    @abstractmethod
    def create_comment(self, repo_name: str, pull_request_id: int, text: str) -> PullRequestComment:
        pass
