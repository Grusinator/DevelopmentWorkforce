from typing import Optional, List

from pydantic import BaseModel

from src.devops_integrations.pull_requests.pull_request_models import PullRequestCommentThreadModel


class TaskExtraInfo(BaseModel):
    pr_comments: List[PullRequestCommentThreadModel] = []
