from datetime import datetime
from typing import Optional, Union

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
    id: Union[int, str]
    source_id: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True


class RepositoryModel(BaseModel):
    id: Union[int, str]  # TODO fix revert to int, there should be no source ids here
    source_id: str
    name: str
    git_url: str
    project: Optional[ProjectModel] = None

    class Config:
        from_attributes = True
