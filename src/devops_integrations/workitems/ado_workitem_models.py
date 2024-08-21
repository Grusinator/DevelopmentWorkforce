from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional

from enum import Enum


class WorkItemStateEnum(str, Enum):
    PENDING = 'pending'  # waiting to be picked up by an agent
    IN_PROGRESS = 'in_progress'  # has been developed on but pr not completed
    COMPLETED = 'completed'
    FAILED = 'failed'

    @classmethod
    def choices(cls):
        return [(key.value, key.name.replace("_", " ").title()) for key in cls]


class WorkItemBaseModel(BaseModel):
    # Define all fields except 'id'
    title: str
    type: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = []
    state: str
    acceptance_criteria: Optional[str] = None


class WorkItemModel(WorkItemBaseModel):
    # This model includes 'id' and is used in contexts where 'id' is known/required
    source_id: int

    class Config:
        from_attributes = True

    @staticmethod
    def fields():
        return [(name, field.type_) for name, field in WorkItemModel.__annotations__.items()]

    def __str__(self):
        return f"{self.source_id} {self.title}"

    def pretty_print(self):
        return f"""
        title:
        {self.title}

        desc:
        {self.description}

        tags:
        {self.tags}
        """


class CreateWorkItemInputModel(WorkItemBaseModel):
    # This model is used specifically for creation, no 'id' field needed
    pass


class UpdateWorkItemInputModel(WorkItemBaseModel):
    source_id: int = Field(description="ID of the work item to update")
    title: Optional[str] = None
    type: Optional[str] = None
    state: Optional[str] = None
    acceptance_criteria: Optional[str] = None


class GetWorkItemInputModel(BaseModel):
    id: int = Field(description="ID of the work item to get")


class WorkItemCommentModel(BaseModel):
    id: int
    text: str
    created_by: str
    created_date: datetime
    revised_by: Optional[str] = None
    revised_date: Optional[datetime] = None
