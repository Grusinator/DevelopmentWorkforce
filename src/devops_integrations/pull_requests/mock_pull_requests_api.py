from typing import List, Dict
from src.devops_integrations.pull_requests.base_pull_requests_api import BasePullRequestsApi
from src.devops_integrations.pull_requests.pull_request_models import CreatePullRequestInputModel, PullRequestModel, \
    PullRequestCommentModel, PullRequestCommentThreadModel
from src.devops_integrations.repos.ado_repos_models import RepositoryModel


class MockPullRequestsApi(BasePullRequestsApi):
    def __init__(self):
        self.pull_requests: Dict[int, PullRequestModel] = {}
        self.comments: Dict[int, List[PullRequestCommentThreadModel]] = {}
        self.next_pr_id = 1
        self.next_comment_id = 1

    def create_pull_request(self, repository_id: str, pr_input: CreatePullRequestInputModel) -> int:
        pr_id = self.next_pr_id
        self.next_pr_id += 1
        repository = RepositoryModel(id=repository_id, source_id=repository_id, name="Mock Repo",
                                     url="http://mock.url/repo")
        pull_request = PullRequestModel(
            id=pr_id,
            repository=repository,
            status="open",
            **pr_input.model_dump()
        )
        self.pull_requests[pr_id] = pull_request
        return pr_id

    def get_pull_request(self, repository_id: str, pr_id: int) -> PullRequestModel:
        return self.pull_requests.get(pr_id)

    def list_pull_requests(self, repository_id: str, status: str = None, created_by=None) -> List[PullRequestModel]:
        return [pr for pr in self.pull_requests.values() if pr.repository.id == repository_id]

    def approve_pull_request(self, repo_name: str, pr_id: int) -> None:
        if pr_id in self.pull_requests:
            self.pull_requests[pr_id].status = "approved"

    def abandon_pull_request(self, repo_name: str, pr_id: int) -> None:
        if pr_id in self.pull_requests:
            self.pull_requests[pr_id].status = "abandoned"

    def add_pull_request_comment(self, repo_name: str, pr_id: int, content: str) -> int:
        comment_id = self.next_comment_id
        self.next_comment_id += 1
        comment = PullRequestCommentModel(id=comment_id, content=content)
        if pr_id not in self.comments:
            self.comments[pr_id] = []
        self.comments[pr_id].append(PullRequestCommentThreadModel(id=comment_id, comments=[comment]))
        return comment_id

    def get_pull_request_comments(self, repo_name: str, pull_request_id: int) -> List[PullRequestCommentThreadModel]:
        return self.comments.get(pull_request_id, [])

    def run_build(self, pr_id: int) -> int:
        return 1

    def get_build_status(self, pr_id: int) -> str:
        return "success"

    def create_comment(self, repo_name: str, pull_request_id: int, text: str, thread_id=None) -> PullRequestCommentModel:
        comment_id = self.next_comment_id
        self.next_comment_id += 1
        comment = PullRequestCommentModel(id=comment_id, content=text)
        if pull_request_id not in self.comments:
            self.comments[pull_request_id] = []
        self.comments[pull_request_id].append(PullRequestCommentThreadModel(id=comment_id, comments=[comment]))
        return comment
