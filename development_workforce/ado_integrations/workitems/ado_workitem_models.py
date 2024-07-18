from pydantic import BaseModel, Field
from typing import List, Optional


class AdoWorkItemBase(BaseModel):
    # Define all fields except 'id'
    title: str
    type: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = []
    state: str


class AdoWorkItem(AdoWorkItemBase):
    # This model includes 'id' and is used in contexts where 'id' is known/required
    id: int

    @staticmethod
    def fields():
        return [(name, field.type_) for name, field in AdoWorkItem.__annotations__.items()]

    @staticmethod
    def from_api(api_response: dict) -> "AdoWorkItem":
        fields = api_response.get("fields", {})
        assigned_to = fields.get("System.AssignedTo", {}).get("displayName") if fields.get(
            "System.AssignedTo") else None

        tags = fields.get("System.Tags", "")
        tags_list = tags.split("; ") if tags else []

        work_item = AdoWorkItem(
            id=api_response.get("id"),
            title=fields.get("System.Title"),
            type=fields.get("System.WorkItemType"),
            description=fields.get("System.Description"),
            assigned_to=assigned_to,
            tags=tags_list
        )
        return work_item


class CreateWorkItemInput(AdoWorkItemBase):
    # This model is used specifically for creation, no 'id' field needed
    pass


class UpdateWorkItemInput(AdoWorkItemBase):
    id: int = Field(description="ID of the work item to update")
    title: Optional[str] = None
    type: Optional[str] = None
    state: Optional[str] = None


class GetWorkItemInput(BaseModel):
    id: int = Field(description="ID of the work item to get")
