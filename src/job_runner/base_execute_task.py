from abc import ABC, abstractmethod
from typing import Any

from loguru import logger
from pydantic import BaseModel

from src.crew.models import AutomatedTaskResult


class BaseExecuteTask(ABC):
    name: str
    input_model: BaseModel

    def __init__(self):
        if not hasattr(self, 'name'):
            raise NotImplementedError("Derived classes must define a 'name' class field")
        if not hasattr(self, 'input_model') and issubclass(self.input_model, BaseModel):
            raise NotImplementedError("Derived classes must define a 'input_model' class field")

    @abstractmethod
    def _execute(self, *args: Any, **kwargs: Any) -> AutomatedTaskResult:
        pass

    def run(self, encoded_args: str) -> AutomatedTaskResult:
        input_model = self.input_model.model_validate_json(encoded_args)
        logger.info(f"running task: {self.name}, with input modelInput model: {input_model}")
        result = self._execute(input_model)
        logger.info(f"task {self.name} completed with result: {result}")
        return result
