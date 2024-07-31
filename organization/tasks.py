# tasks.py
from typing import Dict
from celery import shared_task
from loguru import logger
from organization.models import Repository, Agent
from organization.schemas import AgentModel
from organization.services.fetch_new_tasks import TaskFetcherAndScheduler
from src.devops_integrations.repos.ado_repos_models import Repository
from src.devops_integrations.workitems.ado_workitem_models import WorkItem
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi
from src.task_automation import TaskAutomation


@shared_task(name='organization.tasks.execute_task')
def execute_task(agent: Dict, repo: Dict, work_item: Dict):
    agent = AgentModel(**agent)
    repo = Repository(**repo)
    task = WorkItem(**work_item)
    logger.debug(f"running task: {task}")
    task_automation = TaskAutomation(repo, agent)
    task_automation.develop_on_task(task, repo)


@shared_task
def fetch_new_workitems_periodically():
    agents = Agent.objects.filter(status='working')
    for agent in agents:
        repos = Repository.objects.filter(agentrepoconnection__agent=agent, agentrepoconnection__enabled=True)
        for repo in repos:
            wf = TaskFetcherAndScheduler(agent, repo)
            wf.fetch_new_workitems(agent, repo)
