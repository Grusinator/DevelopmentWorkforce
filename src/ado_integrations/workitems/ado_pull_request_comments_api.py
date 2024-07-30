from azure.devops.connection import Connection
from azure.devops.v7_1.git.models import GitPullRequestCommentThread, Comment
from msrest.authentication import BasicAuthentication
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


class PullRequestComment(BaseModel):
    id: int
    text: str
    created_by: str
    created_date: datetime


class PullRequestCommentThread(BaseModel):
    id: int
    comments: List[PullRequestComment]
    status: Optional[str] = None
    published_date: Optional[datetime] = None

class ADOPullRequestCommentsApi:
    def __init__(self, pat, ado_org_name, project_name, repo_name):
        self.organization_url = "https://dev.azure.com/" + ado_org_name
        self.personal_access_token = pat
        self.project_name = project_name
        self.repo_name = repo_name
        credentials = BasicAuthentication('', self.personal_access_token)
        self.connection = Connection(base_url=self.organization_url, creds=credentials)
        self.client = self.connection.clients.get_git_client()

    def list_comments(self, pull_request_id: int) -> List[PullRequestCommentThread]:
        comment_threads = self.client.get_threads(
            repository_id=self.repo_name,
            pull_request_id=pull_request_id,
            project=self.project_name
        )
        threads = []
        for thread in comment_threads:
            comments = [self._from_ado(comment, thread.id) for comment in thread.comments]
            threads.append(PullRequestCommentThread(
                id=thread.id,
                comments=comments,
                status=thread.status,
                published_date=thread.published_date
            ))
        return threads

    def create_comment(self, pull_request_id: int, text: str) -> PullRequestComment:
        new_comment = Comment(content=text)
        comment_thread = GitPullRequestCommentThread(comments=[new_comment])
        created_thread = self.client.create_thread(
            comment_thread,
            self.repo_name,
            pull_request_id,
            project=self.project_name
        )
        created_comment = created_thread.comments[0]
        return self._from_ado(created_comment, created_thread.id)

    def _from_ado(self, comment: Comment, thread_id: int) -> PullRequestComment:
        """Converts an Azure DevOps PullRequestComment object to a Pydantic model."""
        return PullRequestComment(
            id=comment.id,
            text=comment.content,
            created_by=comment.author.display_name if comment.author else None,
            created_date=comment.published_date,
            thread_id=thread_id
        )