from abc import ABC, abstractmethod

from pydantic import BaseModel

from src.crew.models import AutomatedTaskResult


class BaseJobScheduler(ABC):
    @abstractmethod
    def schedule_job(self, job_name: str, job_id: str, input_model: BaseModel) -> str:
        pass

    @abstractmethod
    def get_job_result(self, job_id: str) -> AutomatedTaskResult:
        pass

    @abstractmethod
    def connect_job_completion_handler(self, handler):
        pass

    @abstractmethod
    def connect_job_start_handler(self, handler):
        pass
