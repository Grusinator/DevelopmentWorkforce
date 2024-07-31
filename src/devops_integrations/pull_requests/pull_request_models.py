from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from src.devops_integrations.repos.ado_repos_models import RepositoryModel


class CreatePullRequestInputModel(BaseModel):
    source_branch: str
    target_branch: Optional[str] = "main"
    title: str
    description: Optional[str] = None


class ReviewerModel(BaseModel):
    source_id: str
    display_name: str
    vote: int


class PullRequestModel(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    source_branch: str
    target_branch: str
    status: str
    repository: RepositoryModel
    reviewers: Optional[List[ReviewerModel]] = []


class PullRequestCommentModel(BaseModel):
    id: int
    text: str
    created_by: str
    created_date: datetime


class PullRequestCommentThreadModel(BaseModel):
    id: int
    comments: List[PullRequestCommentModel]
    status: Optional[str] = None
    published_date: Optional[datetime] = None
