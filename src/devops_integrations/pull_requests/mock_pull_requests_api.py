import os
from datetime import datetime

from typing import List
from src.devops_integrations.pull_requests.base_pull_requests_api import BasePullRequestsApi
from src.devops_integrations.pull_requests.pull_request_models import CreatePullRequestInputModel, PullRequestModel, \
    PullRequestCommentModel, PullRequestCommentThreadModel
from src.devops_integrations.repos.ado_repos_models import RepositoryModel

AI_USER_NAME = os.getenv("AI_USER_NAME")


class MockPullRequestsApi(BasePullRequestsApi):
    def __init__(self):
        self.pull_requests: List[PullRequestModel] = []
        self.comment_threads: List[PullRequestCommentThreadModel] = []
        self.next_pr_id = 1
        self.next_comment_id = 1

    def create_pull_request(self, repository_id: str, pr_input: CreatePullRequestInputModel) -> PullRequestModel:
        pr_id = self.next_pr_id
        self.next_pr_id += 1
        repository = RepositoryModel(id=repository_id, source_id=repository_id, name="Mock Repo",
                                     url="http://mock.url/repo")
        pull_request = PullRequestModel(
            id=pr_id,
            repository=repository,
            status="open",
            created_by_name=AI_USER_NAME,
            **pr_input.model_dump()
        )
        self.pull_requests.append(pull_request)
        return pull_request

    def get_pull_request(self, repository_id: str, pr_id: int) -> PullRequestModel:
        return next((pr for pr in self.pull_requests if pr.id == pr_id), None)

    def list_pull_requests(self, repository_id: str, status: str = None, created_by=None) -> List[PullRequestModel]:
        return [pr for pr in self.pull_requests if
                pr.repository.source_id == repository_id
                and (pr.status == status or not status)
                and (pr.created_by_name == created_by or not created_by)]

    def approve_pull_request(self, repo_name: str, pr_id: int) -> None:
        pr = next((pr for pr in self.pull_requests if pr.id == pr_id), None)
        if pr:
            pr.status = "approved"

    def abandon_pull_request(self, repo_name: str, pr_id: int) -> None:
        pr = next((pr for pr in self.pull_requests if pr.id == pr_id), None)
        if pr:
            pr.status = "abandoned"

    def create_comment(self, repo_name: str, pull_request_id: int, text: str,
                       thread_id=None) -> PullRequestCommentModel:
        comment_id = self.next_comment_id
        self.next_comment_id += 1
        comment = PullRequestCommentModel(id=comment_id, text=text, created_by=AI_USER_NAME,
                                          created_date=datetime.now())
        thread = next((t for t in self.comment_threads if t.id == thread_id), None)
        if not thread:
            thread = PullRequestCommentThreadModel(id=comment_id, comments=[comment])
            self.comment_threads.append(thread)
        else:
            thread.comments.append(comment)
        return comment

    def get_pull_request_comments(self, repo_name: str, pull_request_id: int) -> List[PullRequestCommentThreadModel]:
        return [t for t in self.comment_threads if t.pull_request_source_id == pull_request_id]

    def run_build(self, pr_id: int) -> int:
        return 1

    def get_build_status(self, pr_id: int) -> str:
        return "success"
