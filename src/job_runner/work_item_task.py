import base64
import json

from organization.schemas import AgentModel
from src.crew.models import AutomatedTaskResult
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.job_runner.base_execute_task import BaseExecuteTask
from src.task_automation import TaskAutomation


class ExecuteTaskWorkItemHandler(BaseExecuteTask):
    name = 'execute_task_workitem'

    def _decode_and_validate_args(self, encoded_args):
        args, kwargs = self.args_as_string_decode(encoded_args)


        if len(args) != 3:
            raise ValueError("Expected 3 arguments for execute_task_workitem")

        validated_args = [
            AgentModel.model_validate(args[0]),
            RepositoryModel.model_validate(args[1]),
            WorkItemModel.model_validate(args[2])
        ]
        return validated_args, kwargs

    def decode_args(self, encoded_args):
        return

    def _execute(self, agent: AgentModel, repo: RepositoryModel, work_item: WorkItemModel) -> AutomatedTaskResult:
        task_automation = TaskAutomation(repo, agent)
        return task_automation.develop_on_task(work_item, repo)
