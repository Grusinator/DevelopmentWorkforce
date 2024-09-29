import base64
import json

from pydantic import BaseModel

from organization.schemas import AgentModel
from src.crew.models import AutomatedTaskResult
from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.job_runner.base_execute_task import BaseExecuteTask
from src.task_automation import TaskAutomation

class ExecuteTaskPRFeedbackInputModel(BaseModel):
    agent: AgentModel
    repo: RepositoryModel
    pr: PullRequestModel
    work_item: WorkItemModel

class ExecuteTaskPRFeedbackHandler(BaseExecuteTask):
    name = 'execute_task_pr_feedback'
    input_model = ExecuteTaskPRFeedbackInputModel

    def _execute(self, input_model: ExecuteTaskPRFeedbackInputModel) -> AutomatedTaskResult:
        task_automation = TaskAutomation(input_model.repo, input_model.agent)
        return task_automation.update_pr_from_feedback(input_model.pr, input_model.work_item)
