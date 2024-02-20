from pydantic import BaseModel, Field
from typing import List, Optional



class AdoWorkItemBase(BaseModel):
    # Define all fields except 'id'
    title: str
    type: str = "Task"
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = []

class AdoWorkItem(AdoWorkItemBase):
    # This model includes 'id' and is used in contexts where 'id' is known/required
    id: int

    @staticmethod
    def fields():
        return [(name, field.type_) for name, field in AdoWorkItem.__annotations__.items()]
    

class CreateWorkItemInput(AdoWorkItemBase):
    # This model is used specifically for creation, no 'id' field needed
    pass

class UpdateWorkItemInput(AdoWorkItemBase):
    id: int = Field(description="ID of the work item to update")
    title: Optional[str] = None
    type: Optional[str] = None
    
