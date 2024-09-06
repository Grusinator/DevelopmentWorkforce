# Import necessary modules
import json
import base64
from typing import Dict, Any
from loguru import logger
from organization.services.job_scheduler.base_job_scheduler import JobScheduler
from src.crew.models import AutomatedTaskResult
from src.job_runner.eager_job_runner import EagerJobRunner


class EagerJobScheduler(JobScheduler):
    def __init__(self, mock=False):
        super().__init__()
        self.mock = mock
        self.results = {}
        self.runner = EagerJobRunner()

    def schedule_job(self, job_name: str, job_id: str, *args, **kwargs) -> str:
        if job_name not in self.runner.task_handlers:
            raise ValueError(f"Unknown job name: {job_name}")

        encoded_args = base64.b64encode(json.dumps({'args': args, 'kwargs': kwargs}).encode()).decode()
        result = self.runner.run_job(job_name, encoded_args)
        self.store_result(job_id, result)
        return job_id

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        return self.results.get(job_id, {"status": "pending"})

    def store_result(self, job_id: str, result: AutomatedTaskResult):
        result_data = {
            'task_id': job_id,
            'result': result.model_dump()
        }
        self.results[job_id] = result_data
        logger.info(f"Result stored with job ID: {job_id}")

    def connect_job_completion_handler(self, handler):
        logger.info("Job completion handler connected")

    def connect_job_start_handler(self, handler):
        logger.info("Job start handler connected")
