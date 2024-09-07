import base64
import json
from abc import ABC, abstractmethod
from typing import Any

from organization.schemas import AgentModel
from src.crew.models import AutomatedTaskResult
from src.devops_integrations.repos.ado_repos_models import RepositoryModel


class BaseExecuteTask(ABC):
    name: str

    def __init__(self):
        if not hasattr(self, 'name'):
            raise NotImplementedError("Derived classes must define a 'name' class field")

    def args_as_string_decode(self, encoded_args: str):
        job_args = json.loads(base64.b64decode(encoded_args).decode())
        args = job_args['args']
        kwargs = job_args['kwargs']
        return args, kwargs


    @abstractmethod
    def _decode_and_validate_args(self, encoded_args: str) -> Any:
        pass


    @abstractmethod
    def _execute(self, *args: Any, **kwargs: Any) -> AutomatedTaskResult:
        pass


    def run(self, encoded_args: str) -> AutomatedTaskResult:
        args, kwargs = self._decode_and_validate_args(encoded_args)
        return self._execute(*args, **kwargs)
