from celery import current_app as app
from loguru import logger

from organization.models import Agent, Repository
from organization.schemas import AgentModel
from src.devops_integrations.devops_factory import DevOpsFactory
from src.devops_integrations.models import ProjectAuthenticationModel, DevOpsSource
from src.devops_integrations.repos.ado_repos_models import RepositoryModel


class TaskFetcherAndScheduler:
    def __init__(self, agent: AgentModel, repo: RepositoryModel, devops_source: DevOpsSource = DevOpsSource.ADO):
        project_auth = ProjectAuthenticationModel(pat=agent.pat, ado_org_name=agent.organization_name,
                                                  project_name=repo.project.name)
        devops_factory = DevOpsFactory(project_auth, devops_source=devops_source)
        self.workitems_api = devops_factory.get_workitems_api()
        self.repos_api = devops_factory.get_repos_api()
        self.pull_requests_api = devops_factory.get_pullrequests_api()

    def fetch_new_workitems(self, agent: AgentModel, repo: RepositoryModel):
        new_tasks = self.workitems_api.list_work_items(assigned_to=agent.agent_user_name, state="New")
        for task in new_tasks:
            logger.debug(f"task started: {task}")
            app.send_task('organization.tasks.execute_task',
                          args=[agent.model_dump(), repo.model_dump(), task.model_dump()])

    def fetch_pull_requests_waiting_for_author(self, agent: AgentModel, repo: RepositoryModel):
        prs = self.pull_requests_api.list_pull_requests(repository_id=repo.source_id)
        print(prs)
        pull_requests = self.pull_requests_api.list_pull_requests(repository_id=repo.source_id,
                                                                  created_by=agent.agent_user_name
                                                                  # status="Waiting for Author"
                                                                  )
        return pull_requests
