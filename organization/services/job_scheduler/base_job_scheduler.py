from abc import ABC, abstractmethod

from pydantic import BaseModel

from src.crew.models import AutomatedTaskResult


class BaseJobScheduler(ABC):
    @abstractmethod
    def schedule_job(self, job_name: str, job_id: str, input_model: BaseModel):
        pass

    @abstractmethod
    async def get_job_result(self, job_id: str) -> AutomatedTaskResult:
        pass
