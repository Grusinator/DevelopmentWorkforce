from typing import Dict

from src.crew.models import AutomatedTaskResult
from src.job_runner.base_job_runner import BaseJobRunner


class EagerJobRunner(BaseJobRunner):

    def __init__(self):
        self.results: Dict[str, AutomatedTaskResult] = {}

    def _store_result(self, job_id, result: AutomatedTaskResult):
        # Store result logic can be implemented here if needed
        self.results[job_id] = result

