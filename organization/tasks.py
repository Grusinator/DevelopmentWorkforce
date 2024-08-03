# tasks.py
from typing import Dict

from celery import shared_task
from loguru import logger

from organization.models import Repository, Agent, WorkItem
from organization.schemas import AgentModel
from organization.services.fetch_new_tasks import TaskFetcherAndScheduler
from organization.services.task_updater_hook import TaskUpdater
from src.devops_integrations.models import DevOpsSource
from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.task_automation import TaskAutomation


@shared_task(name='organization.tasks.execute_task_workitem')
def execute_task_workitem(agent: Dict, repo: Dict, work_item: Dict, mock=False):
    agent_md = AgentModel.model_validate(agent)
    repo_md = RepositoryModel.model_validate(repo)
    work_item_md = WorkItemModel.model_validate(work_item)
    logger.debug(f"running task: {work_item_md}")
    task_updater = TaskUpdater(Agent.objects.get(id=agent_md.id))
    task_automation = TaskAutomation(repo_md, agent_md, task_updater, devops_source=DevOpsSource.MOCK if mock else None)
    task_automation.develop_on_task(work_item_md, repo_md)


@shared_task(name='organization.tasks.execute_task_pr_feedback')
def execute_task_pr_feedback(agent: Dict, repo: Dict, pr: Dict):
    agent_md = AgentModel.model_validate(agent)
    repo_md = RepositoryModel.model_validate(repo)
    pull_request = PullRequestModel.model_validate(pr)
    logger.debug(f"running review on pr: {pr}")
    task_updater = TaskUpdater(Agent.objects.get(id=agent_md.id))
    task_automation = TaskAutomation(repo_md, agent_md, task_updater)
    work_item = WorkItem.objects.get(pull_request_source_id=pull_request.id)
    task_automation.update_pr_from_feedback(pull_request, work_item)


@shared_task(name='fetch_new_tasks_periodically')
def fetch_new_tasks_periodically(mock=False):
    logger.info("fetching new tasks from devops")
    agents = Agent.objects.filter(status='working')
    for agent in agents:
        repos = Repository.objects.filter(agentrepoconnection__agent=agent, agentrepoconnection__enabled=True)
        agent_md = AgentModel.model_validate(agent)
        for repo in repos:
            repo_md = RepositoryModel.model_validate(repo)
            wf = TaskFetcherAndScheduler(agent_md, repo_md, devops_source=DevOpsSource.MOCK if mock else None)
            wf.fetch_new_workitems(agent_md, repo_md)
            wf.fetch_pull_requests_waiting_for_author(agent_md, repo_md)
