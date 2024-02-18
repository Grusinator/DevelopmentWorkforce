from pydantic import BaseModel
from typing import List

class AdoWorkItem(BaseModel):
    id: int
    title: str
    description: str
    assigned_to: str
    tags: List[str]