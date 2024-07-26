from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]

class AgentWorkSessionModel(BaseModel):
    id: int
    agent_id: int
    start_time: datetime
    end_time: Optional[datetime]

class AgentModel(BaseModel):
    id: int
    user: UserModel
    pat: str
    status: str
    organization_name: str
    agent_user_name: str
    active_work_session: Optional[AgentWorkSessionModel]