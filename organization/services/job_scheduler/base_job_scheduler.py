from abc import ABC, abstractmethod
from typing import Dict, Any

class JobScheduler(ABC):
    @abstractmethod
    def schedule_job(self, job_name: str, job_id: str, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def connect_job_completion_handler(self, handler):
        pass

    @abstractmethod
    def connect_job_start_handler(self, handler):
        pass
