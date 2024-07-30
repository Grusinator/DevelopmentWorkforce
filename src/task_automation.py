# task_automation.py
import os
import uuid
from pathlib import Path

import loguru

from organization.schemas import AgentModel
from src.ado_integrations.repos.ado_repos_models import CreatePullRequestInput, RepositoryModel
from src.ado_integrations.repos.ado_repos_wrapper_api import ADOReposWrapperApi
from src.ado_integrations.workitems.ado_workitem_models import WorkItem, UpdateWorkItemInput
from src.ado_integrations.workitems.ado_workitems_comments_api import ADOWorkitemsCommentsApi
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi
from src.git_manager import GitManager
from src.local_development_session import LocalDevelopmentSession


class TaskAutomation:
    def __init__(self, repo: RepositoryModel, agent: AgentModel):
        self.ado_workitem_comments_api = ADOWorkitemsCommentsApi(agent.pat, agent.organization_name, repo.project.name)
        self.ado_workitems_api = ADOWorkitemsWrapperApi(agent.pat, agent.organization_name, repo.project.name)
        self.ado_repos_api = ADOReposWrapperApi(agent.pat, agent.organization_name, repo.project.name, repo.name)
        self.dev_session = LocalDevelopmentSession()
        # TODO THis LocalDevelopmentSession might only be temp until i have refactored the
        #  other classes to not take in personal info
        self.git_manager = GitManager()
        self.user_name = agent.agent_user_name
        self.root_workspace_dir = Path(os.getenv("WORKSPACE_DIR"))

    def get_new_tasks(self, state="New"):
        return self.ado_workitems_api.list_work_items(assigned_to=self.user_name, state=state)

    def develop_on_task(self, work_item: WorkItem, repo: RepositoryModel):
        work_item_input = UpdateWorkItemInput(source_id=work_item.source_id, state="Active")
        self.ado_workitems_api.update_work_item(work_item_input)

        repo_dir, branch_name = self._setup_development_env(work_item, repo)
        result = self.dev_session.local_development_on_workitem(work_item, repo_dir)

        if result.succeeded:
            self.push_changes_and_create_pull_request(work_item, repo_dir, branch_name)
        else:
            self.reply_back_failed_response(work_item)

    def reply_back_failed_response(self, work_item):
        self.ado_workitem_comments_api.create_comment(work_item.source_id, "Task could not be completed.")
        loguru.logger.error(f"Task could not be completed: {work_item.title}")

    def push_changes_and_create_pull_request(self, work_item, repo_dir, branch_name):
        self.git_manager.push_changes(repo_dir, branch_name, work_item.title)
        pull_request_input = CreatePullRequestInput(title=work_item.title, source_branch=branch_name,
                                                    description=work_item.description)
        self.ado_repos_api.create_pull_request(pull_request_input)
        loguru.logger.info(f"Created pull request for task: {work_item.title}")

    def _setup_development_env(self, work_item: WorkItem, repo: RepositoryModel):
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
