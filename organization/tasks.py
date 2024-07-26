# tasks.py
from typing import Dict
from celery import shared_task
from loguru import logger
from organization.models import Repository, Agent
from organization.schemas import AgentModel
from organization.services.fetch_new_tasks import WorkItemFetcher
from src.ado_integrations.repos.ado_repos_models import RepositoryModel
from src.ado_integrations.workitems.ado_workitem_models import WorkItem
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi
from src.task_automation import TaskAutomation


@shared_task(name='organization.tasks.execute_task')
def execute_task(agent: Dict, repo: Dict, work_item: Dict):
    agent = AgentModel(**agent)
    repo = RepositoryModel(**repo)
    task = WorkItem(**work_item)
    logger.debug(f"running task: {task}")
    task_automation = TaskAutomation(repo, agent)
    task_automation.process_task(task)


@shared_task
def fetch_new_workitems_periodically():
    agents = Agent.objects.filter(status='working')
    for agent in agents:
        repos = Repository.objects.filter(agentrepoconnection__agent=agent, agentrepoconnection__enabled=True)
        for repo in repos:
            api = ADOWorkitemsWrapperApi(agent.pat, agent.organization_name, repo.project.name)
            wf = WorkItemFetcher(api)  # TODO design these classes without user info, and parse it along.
            wf.fetch_new_workitems(agent, repo)
