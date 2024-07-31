from celery import current_app as app
from loguru import logger

from organization.models import Agent, Repository
from organization.schemas import AgentModel
from src.devops_integrations.devops_factory import DevOpsFactory
from src.devops_integrations.models import ProjectAuthentication, DevOpsSource
from src.devops_integrations.repos.ado_repos_models import Repository


class TaskFetcherAndScheduler:
    def __init__(self, agent: Agent, repo: Repository, devops_source: DevOpsSource = DevOpsSource.ADO):
        project_auth = ProjectAuthentication(pat=agent.pat, ado_org_name=agent.organization_name,
                                             project_name=repo.project.name)
        devops_factory = DevOpsFactory(project_auth, devops_source=devops_source)
        self.workitems_api = devops_factory.get_workitems_api()
        self.repos_api = devops_factory.get_repos_api()
        self.pull_requests_api = devops_factory.get_pullrequests_api()

    def fetch_new_workitems(self, agent: Agent, repo: Repository):
        new_tasks = self.workitems_api.list_work_items(assigned_to=agent.agent_user_name, state="New")
        agent_md = AgentModel.model_validate(agent)
        repo_md = Repository.model_validate(repo)
        for task in new_tasks:
            logger.debug(f"task started: {task}")
            app.send_task('organization.tasks.execute_task',
                          args=[agent_md.model_dump(), repo_md.model_dump(), task.model_dump()])

    def fetch_pull_requests_waiting_for_author(self, agent: Agent, repo: Repository):
        pull_requests = self.pull_requests_api.list_pull_requests(repository_id=repo.source_id,
                                                                  created_by=agent.agent_user_name,
                                                                  status="Waiting for Author")
