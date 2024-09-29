# Import necessary modules
from typing import Dict, Any
from loguru import logger
from pydantic import BaseModel

from organization.services.job_scheduler.base_job_scheduler import BaseJobScheduler
from src.crew.models import AutomatedTaskResult
from src.job_runner.eager_job_runner import EagerJobRunner


class EagerJobScheduler(BaseJobScheduler):
    def __init__(self, mock=False):
        super().__init__()
        self.mock = mock
        self.results = {}
        self.runner = EagerJobRunner()

    def schedule_job(self, job_name: str, job_id: str, input_model: BaseModel) -> str:
        input_model_json = input_model.model_dump_json()
        self.runner.run_job(job_name, job_id, input_model_json)
        return job_id

    def get_job_result(self, job_id: str) -> AutomatedTaskResult:
        return self.runner.results.get(job_id)

    def connect_job_completion_handler(self, handler):
        logger.info("Job completion handler connected")

    def connect_job_start_handler(self, handler):
        logger.info("Job start handler connected")
