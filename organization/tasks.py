# tasks.py

from celery import shared_task
from loguru import logger

from organization.models import Repository, Agent
from organization.schemas import AgentModel
from organization.services.task_fetcher_and_scheduler import TaskFetcherAndScheduler
from src.devops_integrations.models import DevOpsSource
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from development_workforce.celery import celery_worker


@shared_task(name='fetch_new_tasks_periodically')
def fetch_new_tasks_periodically(mock=False):
    logger.info("fetching new tasks from devops")
    agents = Agent.objects.filter(status='working')
    for agent in agents:
        repos = Repository.objects.filter(agentrepoconnection__agent=agent, agentrepoconnection__enabled=True)
        agent_md = AgentModel.model_validate(agent)
        for repo in repos:
            repo_md = RepositoryModel.model_validate(repo)
            devops_source = DevOpsSource.MOCK if mock else DevOpsSource.ADO
            wf = TaskFetcherAndScheduler(agent_md, repo_md, devops_source)
            wf.fetch_new_workitems(agent_md, repo_md)
            wf.fetch_pull_requests_waiting_for_author(agent_md, repo_md)

celery_worker.setup_cron_job('fetch_new_workitems_15_sec', fetch_new_tasks_periodically.__name__, 15)