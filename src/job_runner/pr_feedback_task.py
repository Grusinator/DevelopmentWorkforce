import base64
import json

from organization.schemas import AgentModel
from src.crew.models import AutomatedTaskResult
from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.job_runner.base_execute_task import BaseExecuteTask
from src.task_automation import TaskAutomation


class ExecuteTaskPRFeedbackHandler(BaseExecuteTask):
    name = 'execute_task_pr_feedback'

    def _decode_and_validate_args(self, encoded_args: str):
        args, kwargs = self.args_as_string_decode(encoded_args)

        if len(args) != 4:
            raise ValueError("Expected 4 arguments for execute_task_pr_feedback")

        validated_args = [
            AgentModel.model_validate(args[0]),
            RepositoryModel.model_validate(args[1]),
            PullRequestModel.model_validate(args[2]),
            WorkItemModel.model_validate(args[3])
        ]
        return validated_args, kwargs

    def _execute(self, agent: AgentModel, repo: RepositoryModel, pr: PullRequestModel,
                 work_item: WorkItemModel) -> AutomatedTaskResult:
        task_automation = TaskAutomation(repo, agent)
        return task_automation.update_pr_from_feedback(pr, work_item)
