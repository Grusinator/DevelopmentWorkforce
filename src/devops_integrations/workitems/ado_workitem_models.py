from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional


class WorkItemBase(BaseModel):
    # Define all fields except 'id'
    title: str
    type: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = []
    state: str
    acceptance_criteria: Optional[str] = None


class WorkItem(WorkItemBase):
    # This model includes 'id' and is used in contexts where 'id' is known/required
    source_id: int

    @staticmethod
    def fields():
        return [(name, field.type_) for name, field in WorkItem.__annotations__.items()]

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


class CreateWorkItemInput(WorkItemBase):
    # This model is used specifically for creation, no 'id' field needed
    pass


class UpdateWorkItemInput(WorkItemBase):
    source_id: int = Field(description="ID of the work item to update")
    title: Optional[str] = None
    type: Optional[str] = None
    state: Optional[str] = None
    acceptance_criteria: Optional[str] = None


class GetWorkItemInput(BaseModel):
    id: int = Field(description="ID of the work item to get")


class WorkItemCommentModel(BaseModel):
    id: int
    text: str
    created_by: Optional[str]
    created_date: datetime
    revised_by: Optional[str]
    revised_date: Optional[datetime]
