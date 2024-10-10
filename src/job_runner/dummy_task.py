from pydantic import BaseModel

from src.crew.models import AutomatedTaskResult
from src.job_runner.base_execute_task import BaseExecuteTask


class DummyTaskInputModel(BaseModel):
    string: str


class ExecuteDummyTaskHandler(BaseExecuteTask):
    name = 'dummy_task'
    input_model = DummyTaskInputModel

    def _execute(self, input_model: DummyTaskInputModel) -> AutomatedTaskResult:
        return AutomatedTaskResult(succeeded=True)
