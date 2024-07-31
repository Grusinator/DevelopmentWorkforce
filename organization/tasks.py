# tasks.py
from typing import Dict
from celery import shared_task
from loguru import logger
from organization.models import Repository, Agent
from organization.schemas import AgentModel
from organization.services.fetch_new_tasks import TaskFetcherAndScheduler
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi
from src.task_automation import TaskAutomation


@shared_task(name='organization.tasks.execute_task')
def execute_task(agent: Dict, repo: Dict, work_item: Dict):
    agent_md = AgentModel.model_validate(agent)
    repo_md = RepositoryModel.model_validate(repo)
    task = WorkItemModel(**work_item)
    logger.debug(f"running task: {task}")
    task_automation = TaskAutomation(repo_md, agent_md)
    task_automation.develop_on_task(task, repo_md)


@shared_task
def fetch_new_workitems_periodically():
    agents = Agent.objects.filter(status='working')
    for agent in agents:
        repos = Repository.objects.filter(agentrepoconnection__agent=agent, agentrepoconnection__enabled=True)
        agent_md = AgentModel.model_validate(agent)
        repo_md = RepositoryModel.model_validate(repo)
        for repo in repos:
            wf = TaskFetcherAndScheduler(agent_md, repo_md)
            wf.fetch_new_workitems(agent_md, repo_md)
