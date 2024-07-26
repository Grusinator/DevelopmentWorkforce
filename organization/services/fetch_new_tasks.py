from celery import current_app as app
from loguru import logger

from organization.models import Agent, Repository
from organization.schemas import AgentModel
from src.ado_integrations.repos.ado_repos_models import RepositoryModel
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi


class WorkItemFetcher:
    def __init__(self, api: ADOWorkitemsWrapperApi):
        self.api = api

    def fetch_new_workitems(self, agent: Agent, repo: Repository):
        new_tasks = self.api.list_work_items(assigned_to=agent.agent_user_name, state="New")
        agent_md = AgentModel.model_validate(agent)
        repo_md = RepositoryModel.model_validate(repo)
        for task in new_tasks:
            logger.debug(f"task started: {task}")
            app.send_task('organization.tasks.execute_task',
                          args=[agent_md.model_dump(), repo_md.model_dump(), task.model_dump()])
