from pydantic import BaseModel
from typing import List

class AdoWorkItem(BaseModel):
    id: int
    title: str
    type: str = "Task"
    description: str = None
    assigned_to: str = None
    tags: List[str] = []

    @staticmethod
    def fields():
        return [(name, field.type_) for name, field in AdoWorkItem.__annotations__.items()]