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


class WorkItem(WorkItemBase):
    # This model includes 'id' and is used in contexts where 'id' is known/required
    id: int

    @staticmethod
    def fields():
        return [(name, field.type_) for name, field in WorkItem.__annotations__.items()]

    def __str__(self):
        return f"{self.id} {self.title}"

    @staticmethod
    def from_ado_api(api_response: dict) -> "WorkItem":
        fields = api_response.get("fields", {})
        assigned_to = fields.get("System.AssignedTo", {}).get("displayName") if fields.get(
            "System.AssignedTo") else None

        tags = fields.get("System.Tags", "")
        tags_list = tags.split("; ") if tags else []

        work_item = WorkItem(
            id=api_response.get("id"),
            title=fields.get("System.Title"),
            type=fields.get("System.WorkItemType"),
            description=fields.get("System.Description"),
            assigned_to=assigned_to,
            tags=tags_list
        )
        return work_item


class CreateWorkItemInput(WorkItemBase):
    # This model is used specifically for creation, no 'id' field needed
    pass


class UpdateWorkItemInput(WorkItemBase):
    id: int = Field(description="ID of the work item to update")
    title: Optional[str] = None
    type: Optional[str] = None
    state: Optional[str] = None


class GetWorkItemInput(BaseModel):
    id: int = Field(description="ID of the work item to get")
