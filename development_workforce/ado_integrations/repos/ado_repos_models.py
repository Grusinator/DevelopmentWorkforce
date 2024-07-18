from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreatePullRequestInput(BaseModel):
    source_branch: str
    target_branch: str
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
