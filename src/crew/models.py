from typing import Optional, List, Dict

from pydantic import BaseModel


class TaskResult(BaseModel):
    output: Optional[str] = None
    thread_id: Optional[int] = None
    work_item_id: Optional[int] = None
    task_id: str


class LocalDevelopmentResult(BaseModel):
    succeeded: bool
    token_usage: Optional[int] = None
    task_results: Optional[List[TaskResult]] = []
    error_message: Optional[str] = None


class AutomatedTaskResult(LocalDevelopmentResult):
    pr_id: Optional[int] = None
