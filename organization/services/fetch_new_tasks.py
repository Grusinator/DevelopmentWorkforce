from loguru import logger

from development_workforce.celery import CeleryWorker
from organization.models import WorkItem
from organization.schemas import AgentModel
from src.devops_integrations.devops_factory import DevOpsFactory
from src.devops_integrations.models import ProjectAuthenticationModel, DevOpsSource
from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel
from src.devops_integrations.repos.ado_repos_models import RepositoryModel


class TaskFetcherAndScheduler:
    def __init__(self, agent: AgentModel, repo: RepositoryModel, devops_source: DevOpsSource = DevOpsSource.ADO):
        project_auth = ProjectAuthenticationModel(pat=agent.pat, ado_org_name=agent.organization_name,
                                                  project_name=repo.project.name)
        devops_factory = DevOpsFactory(project_auth, devops_source=devops_source)
        self.workitems_api = devops_factory.get_workitems_api()
        self.repos_api = devops_factory.get_repos_api()
        self.pull_requests_api = devops_factory.get_pull_requests_api()
        self.celery_worker = CeleryWorker()

    def fetch_new_workitems(self, agent: AgentModel, repo: RepositoryModel):
        new_tasks = self.workitems_api.list_work_items(assigned_to=agent.agent_user_name, state="New")
        for task in new_tasks:
            logger.debug(f"task started: {task}")
            self.celery_worker.add_task('execute_task_workitem',
                                        agent.model_dump(), repo.model_dump(), task.model_dump())
        if new_tasks:
            tasks_joined = '\n * '.join([tsk.title for tsk in new_tasks])
            logger.info(f"found new work item tasks: {tasks_joined}")

    def fetch_pull_requests_waiting_for_author(self, agent: AgentModel, repo: RepositoryModel):
        pull_requests = self.pull_requests_api.list_pull_requests(repository_id=repo.source_id,
                                                                  created_by=agent.agent_user_name
                                                                  )
        waiting_for_author_prs = [pr for pr in pull_requests if any(reviewer.vote == -5 for reviewer in pr.reviewers)]

        for pr in waiting_for_author_prs:
            work_item_md = self.get_work_item_related_to_pr(pr)

            self.celery_worker.add_task("execute_task_pr_feedback",
                                        agent.model_dump(), repo.model_dump(), pr.model_dump(),
                                        work_item_md.model_dump())
        if waiting_for_author_prs:
            joined_prs = '\n * '.join([_pr.title for _pr in waiting_for_author_prs])
            logger.info(f"found new pr review tasks: {joined_prs}")

        return waiting_for_author_prs

    def get_work_item_related_to_pr(self, pr: PullRequestModel):
        work_item = WorkItem.objects.get(pull_request_source_id=pr.id)
        work_item_md = self.workitems_api.get_work_item(work_item.source_id)
        return work_item_md
