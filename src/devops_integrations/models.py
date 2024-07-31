from enum import Enum

from pydantic import BaseModel


class ProjectAuthentication(BaseModel):
    pat: str
    ado_org_name: str
    project_name: str


class DevOpsSource(Enum):
    ADO = "ado"
    GITHUB = "github"
    GITLAB = "gitlab"
    MOCK = "mock"
