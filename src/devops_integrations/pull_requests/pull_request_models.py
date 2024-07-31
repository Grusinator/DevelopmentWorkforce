from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from src.devops_integrations.repos.ado_repos_models import Repository


class CreatePullRequestInput(BaseModel):
    source_branch: str
    target_branch: Optional[str] = "main"
    title: str
    description: Optional[str] = None


class PullRequest(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    source_branch: str
    target_branch: str
    status: str
    repository: Repository


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
