from datetime import datetime
from typing import Dict
from loguru import logger
from organization.models import Agent, AgentTask, WorkItem
from organization.schemas import AgentModel
from src.devops_integrations.devops_factory import DevOpsFactory
from src.devops_integrations.models import ProjectAuthenticationModel, DevOpsSource
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.task_automation import TaskAutomation
from development_workforce.celery import celery_worker, CeleryWorker

EXECUTE_TASK_PR_FEEDBACK_NAME = 'execute_task_pr_feedback'
EXECUTE_TASK_WORKITEM_NAME = 'execute_task_workitem'


class TaskFetcherAndScheduler:
    def __init__(self, agent: AgentModel, repo: RepositoryModel, devops_source: DevOpsSource = DevOpsSource.ADO,
                 celery_worker_instance: CeleryWorker = celery_worker):
        project_auth = ProjectAuthenticationModel(pat=agent.pat, ado_org_name=agent.organization_name,
                                                  project_name=repo.project.name)
        devops_factory = DevOpsFactory(project_auth, devops_source)
        self.workitems_api = devops_factory.get_workitems_api()
        self.repos_api = devops_factory.get_repos_api()
        self.pull_requests_api = devops_factory.get_pull_requests_api()
        self.agent = Agent.objects.get(id=agent.id)
        self.celery_worker = celery_worker_instance

        # Connect task completion to handler
        self.celery_worker.connect_task_signals(self._handle_task_completion)

        # Register Celery tasks
        self.celery_worker.register_tasks({
            EXECUTE_TASK_WORKITEM_NAME: self.execute_task_workitem,
            EXECUTE_TASK_PR_FEEDBACK_NAME: self.execute_task_pr_feedback,
        })

    def fetch_new_workitems(self, agent: AgentModel, repo: RepositoryModel):
        new_tasks = self.workitems_api.list_work_items(assigned_to=agent.agent_user_name, state="New")
        for task in new_tasks:
            logger.debug(f"task started: {task}")
            self.schedule_workitem_task(agent, repo, task)

        if new_tasks:
            tasks_joined = '\n * '.join([tsk.title for tsk in new_tasks])
            logger.info(f"found new work item tasks: {tasks_joined}")

    def fetch_pull_requests_waiting_for_author(self, agent: AgentModel, repo: RepositoryModel):
        pull_requests = self.pull_requests_api.list_pull_requests(repository_id=repo.source_id,
                                                                  created_by=agent.agent_user_name)
        waiting_for_author_prs = [pr for pr in pull_requests if any(reviewer.vote == -5 for reviewer in pr.reviewers)]

        for pr in waiting_for_author_prs:
            work_item_md = self.get_work_item_related_to_pr(pr)
            self.schedule_pr_feedback_task(agent, repo, pr, work_item_md)

        if waiting_for_author_prs:
            joined_prs = '\n * '.join([_pr.title for _pr in waiting_for_author_prs])
            logger.info(f"found new pr review tasks: {joined_prs}")

        return waiting_for_author_prs

    def get_work_item_related_to_pr(self, pr: PullRequestModel) -> WorkItemModel:
        work_item = WorkItem.objects.get(pull_request_source_id=pr.id)
        work_item_md = self.workitems_api.get_work_item(work_item.source_id)
        return work_item_md

    def schedule_workitem_task(self, agent: AgentModel, repo: RepositoryModel, work_item):
        work_item_obj, _ = WorkItem.objects.get_or_create(
            work_item_source_id=work_item.source_id,
            defaults={'status': 'active'}
        )

        agent_task = AgentTask.objects.create(
            session=self.agent.active_work_session,
            work_item=work_item_obj,
        )

        celery_worker.add_task(
            EXECUTE_TASK_WORKITEM_NAME,
            str(agent_task.id),
            agent.model_dump(), repo.model_dump(), work_item.model_dump(),

        )

    def schedule_pr_feedback_task(self, agent: AgentModel, repo: RepositoryModel, pr: PullRequestModel, work_item):
        work_item_obj, _ = WorkItem.objects.get_or_create(
            work_item_source_id=work_item.source_id,
            defaults={'status': 'active', 'pull_request_source_id': pr.id}
        )

        agent_task = AgentTask.objects.create(
            session=self.agent.active_work_session,
            work_item=work_item_obj,
            status='in_progress'
        )

        celery_worker.add_task(
            EXECUTE_TASK_PR_FEEDBACK_NAME,
            str(agent_task.id),
            agent.model_dump(), repo.model_dump(), pr.model_dump(), work_item.model_dump(),
        )

    def _handle_task_completion(self, sender, result, **kwargs):
        logger.debug(f"task completion handler called with result: {result}")

        # Retrieve the task_id from the sender
        task_id = int(sender.request.id)

        # Fetch the AgentTask based on the task_id
        try:
            agent_task = AgentTask.objects.get(id=task_id)
            work_item = agent_task.work_item

            # Determine the status based on the task result
            status = 'completed' if result.get('success', False) else 'failed'
            token_usage = result.get('token_usage')

            # Update the work_item and agent_task with the results
            work_item.status = status
            work_item.save()

            agent_task.end_time = datetime.now()
            agent_task.token_usage = token_usage
            agent_task.save()

            logger.info(f"Task {task_id} completed with status: {status}")
        except AgentTask.DoesNotExist:
            logger.error(f"No AgentTask found with task_id: {task_id}")

    @staticmethod
    def execute_task_workitem(agent: Dict, repo: Dict, work_item: Dict, mock=False):
        agent_md = AgentModel.model_validate(agent)
        repo_md = RepositoryModel.model_validate(repo)
        work_item_md = WorkItemModel.model_validate(work_item)
        logger.debug(f"running task: {work_item_md}")
        dev_ops_source = DevOpsSource.MOCK if mock else DevOpsSource.ADO
        task_automation = TaskAutomation(repo_md, agent_md, devops_source=dev_ops_source)
        result = task_automation.develop_on_task(work_item_md, repo_md)
        return result.model_dump()

    @staticmethod
    def execute_task_pr_feedback(agent: Dict, repo: Dict, pr: Dict, work_item: Dict):
        agent_md = AgentModel.model_validate(agent)
        repo_md = RepositoryModel.model_validate(repo)
        pull_request = PullRequestModel.model_validate(pr)
        work_item_md = WorkItemModel.model_validate(work_item)
        logger.debug(f"running review on pr: {pr}")
        task_automation = TaskAutomation(repo_md, agent_md)
        result = task_automation.update_pr_from_feedback(pull_request, work_item_md)
        return result.model_dump()
