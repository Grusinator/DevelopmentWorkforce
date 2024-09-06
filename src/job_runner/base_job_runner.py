from abc import ABC, abstractmethod

from src.crew.models import AutomatedTaskResult
from src.job_runner.pr_feedback_task import ExecuteTaskPRFeedbackHandler
from src.job_runner.work_item_task import ExecuteTaskWorkItemHandler


class BaseJobRunner(ABC):
    task_handlers = (
        ExecuteTaskWorkItemHandler,
        ExecuteTaskPRFeedbackHandler
    )

    def get_task_handler(self, job_name: str):
        return next(handler() for handler in self.task_handlers if handler.name == job_name)

    def run_job(self, job_name: str, encoded_args: str) -> AutomatedTaskResult:
        if job_name not in self.task_handlers:
            raise ValueError(f"Unknown job name: {job_name}")

        handler = self.get_task_handler(job_name)
        result = handler.run(encoded_args)
        self.store_result(result)
        return result

    @abstractmethod
    def store_result(self, result: AutomatedTaskResult):
        pass
