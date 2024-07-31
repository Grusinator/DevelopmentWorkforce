from typing import Optional, Union

from pydantic import BaseModel


class Project(BaseModel):
    id: Union[int, str]
    source_id: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True


class Repository(BaseModel):
    id: Union[int, str]  # TODO fix revert to int, there should be no source ids here
    source_id: str
    name: str
    git_url: Optional[str] = None
    project: Optional[Project] = None

    class Config:
        from_attributes = True