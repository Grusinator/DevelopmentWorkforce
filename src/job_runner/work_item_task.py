import base64
import json

from pydantic import BaseModel

from organization.schemas import AgentModel
from src.crew.models import AutomatedTaskResult
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.job_runner.base_execute_task import BaseExecuteTask
from src.task_automation import TaskAutomation
class ExecuteTaskWorkItemInputModel(BaseModel):
    agent: AgentModel
    repo: RepositoryModel
    work_item: WorkItemModel

class ExecuteTaskWorkItemHandler(BaseExecuteTask):
    name = 'execute_task_workitem'
    input_model = ExecuteTaskWorkItemInputModel

    def _execute(self, input_model: ExecuteTaskWorkItemInputModel) -> AutomatedTaskResult:
        task_automation = TaskAutomation(input_model.repo, input_model.agent)
        return task_automation.develop_on_task(input_model.work_item, input_model.repo)
