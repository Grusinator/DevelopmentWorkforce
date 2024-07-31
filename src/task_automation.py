# task_automation.py
import os
import uuid
from pathlib import Path

import loguru

from organization.schemas import AgentModel
from src.devops_integrations.devops_factory import DevOpsFactory

from src.devops_integrations.models import ProjectAuthenticationModel, DevOpsSource
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.pull_requests.pull_request_models import CreatePullRequestInputModel, PullRequestModel
from src.devops_integrations.repos.ado_repos_api import ADOReposApi
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel, UpdateWorkItemInputModel
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi
from src.git_manager import GitManager
from src.local_development_session import LocalDevelopmentSession


class TaskAutomation:
    def __init__(self, repo: RepositoryModel, agent: AgentModel, devops_source=DevOpsSource.ADO):
        project_auth = ProjectAuthenticationModel(pat=agent.pat, ado_org_name=agent.organization_name,
                                                  project_name=repo.project.name)
        self.devops_factory = DevOpsFactory(project_auth, devops_source)
        self.workitems_api = self.devops_factory.get_workitems_api()
        self.repos_api = self.devops_factory.get_repos_api()
        self.pull_requests_api = self.devops_factory.get_pullrequests_api()
        self.dev_session = LocalDevelopmentSession()
        # TODO THis LocalDevelopmentSession might only be temp until i have refactored the
        #  other classes to not take in personal info
        self.git_manager = GitManager()
        self.user_name = agent.agent_user_name
        self.root_workspace_dir = Path(os.getenv("WORKSPACE_DIR"))

    def develop_on_task(self, work_item: WorkItemModel, repo: RepositoryModel):
        work_item_input = UpdateWorkItemInputModel(source_id=work_item.source_id, state="Active")
        self.workitems_api.update_work_item(work_item_input)

        repo_dir, branch_name = self._setup_development_env(work_item, repo)
        result = self.dev_session.local_development_on_workitem(work_item, repo_dir)

        if result.succeeded:
            self.push_changes_and_create_pull_request(work_item, repo_dir, branch_name, repo)
        else:
            self.reply_back_failed_response(work_item)

    def update_pr_from_feedback(self, pull_request: PullRequestModel, work_item: WorkItemModel):
        comments = self.pull_requests_api.get_pull_request_comments(pull_request.repository.name, pull_request.id)
        repo_dir, branch_name = self._setup_development_env(work_item, pull_request.repository)
        result = self.dev_session.local_development_on_workitem(work_item, repo_dir, comments)
        if result.succeeded:
            self.git_manager.push_changes(repo_dir, branch_name, work_item.title)
            self.pull_requests_api.reset_pull_request_status(pull_request.id)
        else:
            self.reply_back_failed_response(work_item)

    def reply_back_failed_response(self, work_item):
        self.workitems_api.create_comment(work_item.source_id, "Task could not be completed.")
        loguru.logger.error(f"Task could not be completed: {work_item.title}")

    def push_changes_and_create_pull_request(self, work_item, repo_dir, branch_name, repo):
        self.git_manager.push_changes(repo_dir, branch_name, work_item.title)
        self.create_pull_request(branch_name, work_item, repo)

    def create_pull_request(self, branch_name, work_item, repo):
        pull_request_input = CreatePullRequestInputModel(title=work_item.title, source_branch=branch_name,
                                                         description=work_item.description)
        self.pull_requests_api.create_pull_request(repo.source_id, pull_request_input)
        loguru.logger.info(f"Created pull request for task: {work_item.title}")

    def _setup_development_env(self, work_item: WorkItemModel, repo: RepositoryModel):
        branch_name = self._create_branch_name(work_item)
        repo_dir = self.root_workspace_dir / branch_name
        self.git_manager.clone_and_checkout_branch(repo.git_url, repo_dir, branch_name)
        loguru.logger.info(f"Cloned repository to {repo_dir}")
        return repo_dir, branch_name

    def _create_branch_name(self, work_item) -> str:
        guid = str(uuid.uuid4())[:8]
        title = work_item.title.replace(' ', '_')[:20]
        branch_name = f"{work_item.source_id}-{title}-{guid}"
        return branch_name
