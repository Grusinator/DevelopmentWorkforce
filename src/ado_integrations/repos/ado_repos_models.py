from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreatePullRequestInput(BaseModel):
    source_branch: str
    target_branch: Optional[str] = "main"
    title: str
    description: Optional[str] = None


class AdoPullRequest(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    source_branch: str
    target_branch: str
    status: str


class PullRequestComment(BaseModel):
    id: Optional[int]
    content: str
    created_by: Optional[str]
    created_date: Optional[datetime]


class ProjectModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    url: str


class RepositoryModel(BaseModel):
    id: str
    name: str
    git_url: str
