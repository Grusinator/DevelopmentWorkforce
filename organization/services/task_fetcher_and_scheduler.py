import asyncio
from datetime import datetime

from asgiref.sync import sync_to_async
from loguru import logger

from organization.models import Agent, AgentTask, WorkItem, TaskStatusEnum
from organization.schemas import AgentModel
from organization.services.job_scheduler.base_job_scheduler import BaseJobScheduler
from organization.services.job_scheduler.eager_job_scheduler import EagerJobScheduler
from organization.services.job_scheduler.kubernetes_job_scheduler import KubernetesJobScheduler
from src.crew.models import AutomatedTaskResult
from src.devops_integrations.devops_factory import DevOpsFactory
from src.devops_integrations.models import ProjectAuthenticationModel, DevOpsSource
from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel, WorkItemStateEnum
from src.job_runner.pr_feedback_task import ExecuteTaskPRFeedbackInputModel, ExecuteTaskPRFeedbackHandler
from src.job_runner.work_item_task import ExecuteTaskWorkItemInputModel, ExecuteTaskWorkItemHandler


class TaskFetcherAndScheduler:
    def __init__(self, agent: AgentModel, repo: RepositoryModel, devops_source: DevOpsSource = DevOpsSource.ADO,
                 job_scheduler: BaseJobScheduler = KubernetesJobScheduler()):
        project_auth = ProjectAuthenticationModel(pat=agent.pat, ado_org_name=agent.organization_name,
                                                  project_name=repo.project.name)
        devops_factory = DevOpsFactory(project_auth, devops_source)
        self.workitems_api = devops_factory.get_workitems_api()
        self.repos_api = devops_factory.get_repos_api()
        self.pull_requests_api = devops_factory.get_pull_requests_api()
        self.agent = Agent.objects.get(id=agent.id)
        self.job_scheduler = job_scheduler

    def fetch_new_workitems(self, agent: AgentModel, repo: RepositoryModel):
        state_new = WorkItemStateEnum.PENDING
        new_work_items = self.workitems_api.list_work_items(assigned_to=agent.agent_user_name, state=state_new)
        for work_item in new_work_items:
            logger.debug(f"task started: {work_item}")
            asyncio.run(self.schedule_workitem_task(agent, repo, work_item))

        if new_work_items:
            tasks_joined = '\n * '.join([tsk.title for tsk in new_work_items])
            logger.info(f"found new work item tasks: {tasks_joined}")

    def fetch_pull_requests_waiting_for_author(self, agent: AgentModel, repo: RepositoryModel):
        pull_requests = self.pull_requests_api.list_pull_requests(repository_id=repo.source_id,
                                                                  created_by=agent.agent_user_name)
        waiting_for_author_prs = [pr for pr in pull_requests if any(reviewer.vote == -5 for reviewer in pr.reviewers)]

        for pr in waiting_for_author_prs:
            try:
                work_item_md = self.get_work_item_related_to_pr(pr)
            except WorkItem.DoesNotExist:
                logger.error(f"Work item not found for PR {pr}")
                continue
            else:
                asyncio.run(self.schedule_pr_feedback_task(agent, repo, pr, work_item_md))

        if waiting_for_author_prs:
            joined_prs = '\n * '.join([_pr.title for _pr in waiting_for_author_prs])
            logger.info(f"found new pr review tasks: {joined_prs}")

        return waiting_for_author_prs

    def get_work_item_related_to_pr(self, pr: PullRequestModel) -> WorkItemModel:
        work_item = WorkItem.objects.get(pull_request_source_id=pr.id)
        work_item_md = self.workitems_api.get_work_item(work_item.source_id)
        return work_item_md

    async def schedule_workitem_task(self, agent: AgentModel, repo: RepositoryModel, work_item: WorkItemModel):
        agent_task, created = await sync_to_async(self.sync_work_item_and_agent_task)(work_item, "DEV")

        if created:
            logger.info(f"Task {work_item.source_id} scheduled for execution.")
            self.job_scheduler.schedule_job(
                ExecuteTaskWorkItemHandler.name,
                str(agent_task.id),
                input_model=ExecuteTaskWorkItemInputModel(
                    agent=agent,
                    repo=repo,
                    work_item=work_item
                )
            )
            result = await self.job_scheduler.get_job_result(str(agent_task.id))
            await sync_to_async(self.complete_agent_task)(result, agent_task.id)
        else:
            logger.info(f"Task {work_item.source_id} already registered")


    def sync_work_item_and_agent_task(self, work_item: WorkItemModel, agent_task_tag):
        """Syncs the work item and agent task to the db so that we have an updated record of the task.
        For now it does not handle it well if there are multiple iterations (tasks) on the same type of tag.
        eg. DEV and PR. should be handled better later, fx if a pull request has multiple reviews.
        also tasks will be moved to a different session if the agent is working on a different session,
        so not an accurate log of the task.
        """

        wo_defaults = {'state': WorkItemStateEnum.PENDING.value, 'title': work_item.title}
        work_item_obj, _ = WorkItem.objects.update_or_create(source_id=work_item.source_id,
                                                             defaults=wo_defaults)
        agent_task, created = AgentTask.objects.update_or_create(
            work_item=work_item_obj,
            tag=agent_task_tag,
            agent=self.agent,
            defaults=dict(session=self.agent.active_work_session)
        )
        return agent_task, created

    async def schedule_pr_feedback_task(self, agent: AgentModel, repo: RepositoryModel, pr: PullRequestModel,
                                  work_item: WorkItemModel):
        agent_task, created = await sync_to_async(self.sync_work_item_and_agent_task)(work_item, "PR")

        if created:
            self.job_scheduler.schedule_job(
                ExecuteTaskPRFeedbackHandler.name,
                str(agent_task.id),
                input_model=ExecuteTaskPRFeedbackInputModel(
                    agent=agent,
                    repo=repo,
                    pr=pr,
                    work_item=work_item
                )
            )
            result = await self.job_scheduler.get_job_result(str(agent_task.id))
            await sync_to_async(self.complete_agent_task)(result, agent_task.id)
        else:
            logger.info(f"Task {work_item.source_id} already registered")

    @staticmethod
    def _handle_task_picked_up(sender=None, result=None, **kwargs):
        task_id = int(sender.request.id)
        agent_task = AgentTask.objects.get(id=task_id)
        agent_task.status = TaskStatusEnum.IN_PROGRESS
        agent_task.save()
        work_item = WorkItem.objects.get(source_id=agent_task.work_item.source_id)
        work_item.state = WorkItemStateEnum.IN_PROGRESS
        work_item.save()
        logger.info(f"Task {task_id} picked up. AgentTask and WorkItem statuses updated to IN_PROGRESS.")

    @staticmethod
    def complete_agent_task(result: AutomatedTaskResult, task_id: int):
        agent_task = AgentTask.objects.get(id=task_id)
        # Determine the status based on the task result
        task_result = AutomatedTaskResult.model_validate(result)
        agent_task_status = TaskStatusEnum.COMPLETED if task_result.succeeded else TaskStatusEnum.FAILED

        work_item_state = WorkItemStateEnum.COMPLETED if task_result.succeeded else WorkItemStateEnum.FAILED
        work_item: WorkItem = agent_task.work_item
        # Update the work_item and agent_task with the results
        work_item.state = work_item_state
        work_item.pull_request_source_id = task_result.pr_id
        work_item.save()
        # Update the agent task
        agent_task.end_time = datetime.now()
        agent_task.token_usage = task_result.token_usage or 0
        agent_task.status = agent_task_status
        agent_task.save()
        logger.info(f"Task {task_id} completed with status: {agent_task_status}")