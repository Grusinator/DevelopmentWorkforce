# task_automation.py
import os
from time import sleep

from src.ado_integrations.repos.ado_repos_models import CreatePullRequestInput
from src.ado_integrations.repos.ado_repos_wrapper_api import ADOReposWrapperApi
from src.ado_integrations.workitems.ado_workitem_models import WorkItem, UpdateWorkItemInput
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi
from src.crew.crew_task_runner import CrewTaskRunner
from src.git_manager import GitManager
import loguru


class TaskAutomation:
    def __init__(self, repo_url, repo_name, ado_org_name, project_name, pat, user_name):
        self.ado_workitems_api = ADOWorkitemsWrapperApi(pat, ado_org_name, project_name)
        self.ado_repos_api = ADOReposWrapperApi(pat, ado_org_name, project_name, repo_name)
        self.git_manager = GitManager(repo_url)
        self.user_name = user_name

    def get_new_tasks(self, state="New"):
        return self.ado_workitems_api.list_work_items(assigned_to=self.user_name, state=state)

    def process_task(self, work_item: WorkItem):
        work_item_input = UpdateWorkItemInput(id=work_item.id, state="Active")
        self.ado_workitems_api.update_work_item(work_item_input)
        loguru.logger.info(f"Processing task: {work_item.title}")
        workspace_dir = self.git_manager.clone_and_setup(work_item)
        loguru.logger.info(f"Cloned repository to {workspace_dir}")
        self.run_development_crew(work_item, workspace_dir)
        loguru.logger.info(f"Completed task: {work_item.title}")
        branch_name = workspace_dir.name
        self.git_manager.push_changes(workspace_dir, branch_name, work_item.title)
        loguru.logger.info(f"Pushed changes to repository")
        pull_request_input = CreatePullRequestInput(title=work_item.title, source_branch=branch_name,
                                                    description=work_item.description)
        self.ado_repos_api.create_pull_request(pull_request_input)
        loguru.logger.info(f"Created pull request for task: {work_item.title}")
        return workspace_dir

    def run_development_crew(self, work_item, workspace_dir):
        crew_runner = CrewTaskRunner(workspace_dir)
        crew_runner.add_developer_agent()
        crew_runner.add_task_from_work_item(work_item)
        crew_runner.run()
