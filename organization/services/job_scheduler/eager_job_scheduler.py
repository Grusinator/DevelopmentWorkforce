import asyncio

from pydantic import BaseModel

from organization.services.job_scheduler.base_job_scheduler import BaseJobScheduler
from src.crew.models import AutomatedTaskResult
from src.job_runner.eager_job_runner import EagerJobRunner


class EagerJobScheduler(BaseJobScheduler):
    def __init__(self, mock=False):
        super().__init__()
        self.mock = mock
        self.runner = EagerJobRunner()

    async def schedule_job(self, job_name: str, job_id: str, input_model: BaseModel):
        input_model_json = input_model.model_dump_json()
        await asyncio.to_thread(self.runner.run_job, job_name, job_id, input_model_json)
        return job_id

    async def get_job_result(self, job_id: str) -> AutomatedTaskResult:
        # Poll for the result asynchronously
        while job_id not in self.runner.results.keys():
            await asyncio.sleep(1)  # Non-blocking wait

        return self.runner.results[job_id]

