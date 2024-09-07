import base64
import json
from abc import ABC, abstractmethod
from typing import Dict, Any

from pydantic import BaseModel

from src.crew.models import AutomatedTaskResult


class BaseJobScheduler(ABC):
    @abstractmethod
    def schedule_job(self, job_name: str, job_id: str, *args, **kwargs) -> str:
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

    def encode_args(self, args, kwargs) -> str:
        args = [arg.model_dump() if isinstance(arg, BaseModel) else arg for arg in args]
        #kwargs =  {k:v.model_dump() if isinstance(v, BaseModel) else k:v for k, v in kwargs.items()}
        encoded_args = base64.b64encode(json.dumps({'args': args, 'kwargs': kwargs}).encode()).decode()
        return encoded_args
