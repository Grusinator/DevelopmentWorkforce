# task_automation.py
import os
import uuid
from pathlib import Path

from loguru import logger
from organization.schemas import AgentModel
from src.base_task_updater import TaskUpdaterBase
from src.devops_integrations.devops_factory import DevOpsFactory
from src.devops_integrations.models import ProjectAuthenticationModel, DevOpsSource
from src.devops_integrations.pull_requests.pull_request_models import CreatePullRequestInputModel, PullRequestModel
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel, UpdateWorkItemInputModel
from src.git_manager import GitManager
from src.local_development_session import LocalDevelopmentSession, TaskExtraInfo


class TaskAutomation:
    def __init__(self, repo: RepositoryModel, agent: AgentModel, task_updater: TaskUpdaterBase,
                 devops_source=DevOpsSource.ADO):
        self.task_updater = task_updater
        project_auth = ProjectAuthenticationModel(pat=agent.pat, ado_org_name=agent.organization_name,
                                                  project_name=repo.project.name)
        self.devops_factory = DevOpsFactory(project_auth, devops_source)
        self.workitems_api = self.devops_factory.get_workitems_api()
        self.repos_api = self.devops_factory.get_repos_api()
        self.pull_requests_api = self.devops_factory.get_pull_requests_api()
        self.dev_session = LocalDevelopmentSession()
        self.git_manager = GitManager()
        self.user_name = agent.agent_user_name
        self.root_workspace_dir = Path(os.getenv("WORKSPACE_DIR"))

    def develop_on_task(self, work_item: WorkItemModel, repo: RepositoryModel):
        # agent_task_id = self.task_updater.start_agent_task(work_item_id=work_item.source_id, status='in_progress')
        work_item_input = UpdateWorkItemInputModel(source_id=work_item.source_id, state="Active")
        self.workitems_api.update_work_item(work_item_input)

        repo_dir, branch_name = self._setup_development_env(work_item, repo)
        result = self.dev_session.local_development_on_workitem(work_item, repo_dir)

        if result.succeeded:
            pr_id = self._push_changes_and_create_pull_request(work_item, repo_dir, branch_name, repo)
            # self.task_updater.end_agent_task(agent_task_id, status='completed', token_usage=result.token_usage,
            #                                  pull_request_id=pr_id)
        else:
            self._reply_back_failed_response(work_item)
            # self.task_updater.end_agent_task(agent_task_id, status='failed', token_usage=result.token_usage)
        logger.debug("completed develop flow")

    def update_pr_from_feedback(self, pull_request: PullRequestModel, work_item: WorkItemModel):
        # fetch repository again since the git url is not being parsed along. have not figured out why
        repository = self.repos_api.get_repository(pull_request.repository.name)
        # agent_task = self.task_updater.start_agent_task(work_item_id=work_item.source_id,
        #                                                 pull_request_id=pull_request.id, status='in_progress')
        repo_dir, branch_name = self._setup_development_env(work_item, repository)
        comment_threads = self.pull_requests_api.get_pull_request_comments(pull_request.repository.name,
                                                                           pull_request.id)
        extra_info = TaskExtraInfo(pr_comments=comment_threads)
        result = self.dev_session.local_development_on_workitem(work_item, repo_dir, extra_info)
        if result.succeeded:
            self.git_manager.push_changes(repo_dir, branch_name, work_item.title)
            self.pull_requests_api.reset_pull_request_votes(branch_name, pull_request.id)

            self.reply_to_comments(comment_threads, pull_request)
            # self.task_updater.end_agent_task(agent_task, status='completed', token_usage=result.token_usage)
        else:
            self._reply_back_failed_response(work_item)
            # self.task_updater.end_agent_task(agent_task, status='failed', token_usage=result.token_usage)
        logger.debug("completed develop pr flow")

    def reply_to_comments(self, comment_threads, pull_request):
        for thread in comment_threads:
            self.pull_requests_api.create_comment(pull_request.repository.source_id, pull_request.id, "Task completed.",
                                                  thread_id=thread.id)

    def _reply_back_failed_response(self, work_item):
        self.workitems_api.create_comment(work_item.source_id, "Task could not be completed.")
        logger.error(f"Task could not be completed: {work_item.title}")

    def _push_changes_and_create_pull_request(self, work_item, repo_dir, branch_name, repo):
        self.git_manager.push_changes(repo_dir, branch_name, work_item.title)
        return self._create_pull_request(branch_name, work_item, repo)

    def _create_pull_request(self, branch_name, work_item, repo):
        pull_request_input = CreatePullRequestInputModel(title=work_item.title, source_branch=branch_name,
                                                         description=work_item.description)
        pr_id = self.pull_requests_api.create_pull_request(repo.source_id, pull_request_input)
        logger.info(f"Created pull request for task: {work_item.title}")
        return pr_id

    def _setup_development_env(self, work_item: WorkItemModel, repo: RepositoryModel):
        logger.debug("repo issue: " + str(repo.__dict__))
        branch_name = self._create_branch_name(work_item)
        repo_dir = self.root_workspace_dir / branch_name
        self.git_manager.clone_and_checkout_branch(repo.git_url, repo_dir, branch_name)
        logger.info(f"Cloned repository to {repo_dir}")
        return repo_dir, branch_name

    def _create_branch_name(self, work_item) -> str:
        guid = str(uuid.uuid4())[:8]
        title = work_item.title.replace(' ', '_')[:20]
        branch_name = f"{work_item.source_id}-{title}-{guid}"
        return branch_name
