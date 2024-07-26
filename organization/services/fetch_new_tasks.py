from loguru import logger
from celery import current_app as app
from organization.models import Agent, Repository
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi


def fetch_new_workitems(agent: Agent, repo: Repository):
    work_items_api = ADOWorkitemsWrapperApi(agent.pat, agent.organization_name, repo.project.name)
    new_tasks = work_items_api.list_work_items(assigned_to=agent.agent_user_name, state="New")
    for task in new_tasks:
        logger.debug(f"task started: {task}")
        app.send_task('organization.tasks.execute_task', args=[agent.__dict__, repo.__dict__, task.model_dump()])
