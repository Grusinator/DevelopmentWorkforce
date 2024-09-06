from src.crew.models import AutomatedTaskResult
from src.job_runner.base_job_runner import BaseJobRunner


class EagerJobRunner(BaseJobRunner):
    def __init__(self, mock=False):


        self.mock = mock

    def store_result(self, result: AutomatedTaskResult):
        # Store result logic can be implemented here if needed
        pass

    def run_job(self, job_name: str, encoded_args: str) -> AutomatedTaskResult:
        task = self.get_task_handler(job_name)
        result = task.run(encoded_args)
        self.store_result(result)
