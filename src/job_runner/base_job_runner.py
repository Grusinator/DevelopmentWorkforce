from abc import ABC, abstractmethod

from src.crew.models import AutomatedTaskResult
from src.job_runner.base_execute_task import BaseExecuteTask
from src.job_runner.pr_feedback_task import ExecuteTaskPRFeedbackHandler
from src.job_runner.work_item_task import ExecuteTaskWorkItemHandler


class BaseJobRunner(ABC):
    task_handlers = (
        ExecuteTaskWorkItemHandler,
        ExecuteTaskPRFeedbackHandler
    )

    def _get_task_handler(self, job_name: str) -> BaseExecuteTask:
        try:
            return next(handler() for handler in self.task_handlers if handler.name == job_name)
        except StopIteration:
            task_handler_names = [h.name for h in self.task_handlers]
            raise ValueError(f"No tasks exist with that name, try the following: {task_handler_names}")

    def run_job(self, job_name: str, job_id: str, encoded_args: str) -> AutomatedTaskResult:
        handler = self._get_task_handler(job_name)
        result = handler.run(encoded_args)
        self.store_result(job_id, result)
        return result

    @abstractmethod
    def store_result(self, job_id, result: AutomatedTaskResult):
        pass
