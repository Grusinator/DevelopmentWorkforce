from abc import ABC, abstractmethod
from typing import List

from loguru import logger

from src.crew.models import AutomatedTaskResult
from src.job_runner.base_execute_task import BaseExecuteTask
from src.job_runner.dummy_task import ExecuteDummyTaskHandler
from src.job_runner.pr_feedback_task import ExecuteTaskPRFeedbackHandler
from src.job_runner.work_item_task import ExecuteTaskWorkItemHandler


class BaseJobRunner(ABC):
    task_handlers = (
        ExecuteTaskWorkItemHandler,
        ExecuteTaskPRFeedbackHandler,
        ExecuteDummyTaskHandler
    )

    @classmethod
    def get_task_names(cls) -> List[str]:
        return [handler.name for handler in cls.task_handlers]

    @classmethod
    def _get_task_handler(cls, job_name: str) -> BaseExecuteTask:
        try:
            return next(handler() for handler in cls.task_handlers if handler.name == job_name)
        except StopIteration:
            task_handler_names = [h.name for h in cls.task_handlers]
            raise ValueError(f"No tasks exist with that name, try the following: {task_handler_names}")

    def run_job(self, job_name: str, job_id: str, encoded_args: str) -> AutomatedTaskResult:
        try:
            handler = self._get_task_handler(job_name)
            result = handler.run(encoded_args)
        except Exception as e:
            result = AutomatedTaskResult(succeeded=False, error_message=str(e))
            logger.error(f"Job {job_name} failed with error: {e}")
        try:
            self._store_result(job_id, result)
        except Exception as e:
            logger.error(f"Failed to store result for job {job_id} with error: {e}")
            raise e
        return result

    @abstractmethod
    def _store_result(self, job_id, result: AutomatedTaskResult):
        pass
