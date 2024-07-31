from typing import List

from azure.devops.v7_0.git import GitPullRequestCommentThread
from azure.devops.v7_1.git import GitPullRequest, GitPullRequestSearchCriteria
from azure.devops.v7_1.git.models import Comment, CommentThread
from azure.devops.exceptions import AzureDevOpsServiceError
from src.devops_integrations.ado_connection import ADOConnection
from src.devops_integrations.pull_requests.base_pull_requests_api import BasePullRequestsApi
from src.devops_integrations.repos.ado_repos_api import ADOReposApi
from src.devops_integrations.pull_requests.pull_request_models import CreatePullRequestInput, PullRequest, \
    PullRequestComment

from src.devops_integrations.models import ProjectAuthentication

from src.devops_integrations.pull_requests.pull_request_models import PullRequestCommentThread


class ADOPullRequestsApi(ADOConnection, BasePullRequestsApi):
    api_version = "7.1-preview.1"

    def __init__(self, auth: ProjectAuthentication):
        super().__init__(auth)
        self.repo_api = ADOReposApi(auth)

    def get_base_url(self, repo_name: str) -> str:
        return f"https://dev.azure.com/{self.auth.ado_org_name}/{self.auth.project_name}/_apis/git/repositories/{repo_name}"

    def create_pull_request(self, repository_id: str, pr_input: CreatePullRequestInput) -> int:
        pr = GitPullRequest(
            source_ref_name=f"refs/heads/{pr_input.source_branch}",
            target_ref_name=f"refs/heads/{pr_input.target_branch}",
            title=pr_input.title,
            description=pr_input.description
        )
        try:
            created_pr = self.client.create_pull_request(pr, repository_id, self.auth.project_name)
            return created_pr.pull_request_id
        except AzureDevOpsServiceError as e:
            if "TF401179" in str(e):
                search_criteria = GitPullRequestSearchCriteria(
                    source_ref_name=pr.source_ref_name,
                    target_ref_name=pr.target_ref_name,
                    status="active"
                )
                existing_prs = self.client.get_pull_requests(
                    repository_id, search_criteria, project=self.auth.project_name)
                if existing_prs:
                    return existing_prs[0].pull_request_id
            else:
                raise

    def get_pull_request(self, repository_id, pr_id: int) -> PullRequest:
        pr = self.client.get_pull_request(repository_id, pr_id, project=self.auth.project_name)
        return self.to_pull_request(pr)

    def list_pull_requests(self, repository_id: str, status: str = None, created_by=None) -> List[PullRequest]:
        search_criteria = GitPullRequestSearchCriteria(status=status, creator_id=created_by)
        prs = self.client.get_pull_requests(repository_id, search_criteria, project=self.auth.project_name)
        return [self.to_pull_request(pr) for pr in prs]

    def to_pull_request(self, pr) -> PullRequest:
        return PullRequest(
            id=pr.pull_request_id,
            title=pr.title,
            description=pr.description,
            source_branch=pr.source_ref_name,
            target_branch=pr.target_ref_name,
            status=pr.status,
            repository=self.repo_api._to_repository(pr.repository)
        )

    def update_pull_request(self, repo_name: str, pull_request_id: int, **kwargs):
        url = f"{self.get_base_url(repo_name)}/pullrequests/{pull_request_id}?api-version={self.api_version}"
        self.make_request('PATCH', url, json=kwargs)

    def approve_pull_request(self, repo_name: str, pr_id: int) -> None:
        self.update_pull_request(repo_name, pr_id, status="approved")

    def abandon_pull_request(self, repo_name: str, pr_id: int) -> None:
        self.update_pull_request(repo_name, pr_id, status="abandoned")

    def add_pull_request_comment(self, repo_name: str, pr_id: int, content: str) -> int:
        repository_id = self.repo_api.get_repository_id(repo_name)
        comment = Comment(content=content)
        comment_thread = CommentThread(comments=[comment])
        created_thread = self.client.create_thread(comment_thread, repository_id, pr_id, project=self.auth.project_name)
        return created_thread.id

    def get_pull_request_comments(self, repo_name: str, pull_request_id: int) -> List[PullRequestCommentThread]:
        comment_threads = self.client.get_threads(
            repository_id=repo_name,
            pull_request_id=pull_request_id,
            project=self.auth.project_name
        )
        return [self._to_comment_thread(thread) for thread in comment_threads]

    def _to_comment_thread(self, thread):
        return PullRequestCommentThread(
            id=thread.id,
            comments=[self._to_pr_comment(comment) for comment in thread.comments],
            status=thread.status,
            published_date=thread.published_date
        )

    def run_build(self, pr_id: int) -> int:
        build_definition_id = pr_id
        build = {
            'definition': {'id': build_definition_id}
        }
        build = self.build_client.queue_build(build, project=self.auth.project_name)
        return build.id

    def get_build_status(self, pr_id: int) -> str:
        builds = self.build_client.get_builds(project=self.auth.project_name, definitions=[pr_id])
        if not builds:
            return "No builds found"
        build = builds[0]
        return build.status

    def create_comment(self, repo_name, pull_request_id: int, text: str) -> PullRequestComment:
        new_comment = Comment(content=text)
        comment_thread = GitPullRequestCommentThread(comments=[new_comment])
        created_thread = self.client.create_thread(
            comment_thread,
            repo_name,
            pull_request_id,
            project=self.auth.project_name
        )
        created_comment = created_thread.comments[0]
        return self._to_pr_comment(created_comment)

    def _to_pr_comment(self, comment: Comment) -> PullRequestComment:
        return PullRequestComment(
            id=comment.id,
            text=comment.content,
            created_by=comment.author.display_name if comment.author else None,
            created_date=comment.published_date
        )
