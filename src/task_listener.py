import os
from time import sleep

from src.ado_integrations.repos.ado_repos_models import CreatePullRequestInput
from src.ado_integrations.repos.ado_repos_wrapper_api import ADOReposWrapperApi
from src.ado_integrations.workitems.ado_workitem_models import AdoWorkItem, UpdateWorkItemInput
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi
from src.crew.run_crew import CrewTaskRunner
from src.git_manager import GitManager
import loguru


class TaskAutomation:
    def __init__(self):
        self.ado_workitems_api = ADOWorkitemsWrapperApi()
        self.ado_repos_api = ADOReposWrapperApi()
        self.git_manager = GitManager()
        self.ai_crew_runner = CrewTaskRunner()
        self.user_name = os.environ.get("AI_USER_NAME")

    def listen_and_process_tasks(self):
        # Listen for new tasks assigned to the given name
        # This is a placeholder for the actual implementation
        while True:
            self.find_new_task()
            sleep(3)

    def find_new_task(self):
        new_work_items = self.ado_workitems_api.list_work_items(assigned_to=self.user_name)
        for work_item in new_work_items:
            if work_item.assigned_to == self.user_name and work_item.state == 'New':
                return self.process_task(work_item)
            loguru.logger.info(f"No new tasks found for {self.user_name}, going to sleep...")

    def process_task(self, work_item: AdoWorkItem):
        work_item_input = UpdateWorkItemInput(id=work_item.id, state="Active")
        self.ado_workitems_api.update_work_item(work_item_input)
        loguru.logger.info(f"Processing task: {work_item.title}")
        workspace_dir = self.git_manager.clone_and_setup(work_item)
        loguru.logger.info(f"Cloned repository to {workspace_dir}")
        self.ai_crew_runner.run(work_item, workspace_dir)
        loguru.logger.info(f"Completed task: {work_item.title}")
        branch_name = workspace_dir.name
        self.git_manager.push_changes(workspace_dir, branch_name, work_item.title)
        loguru.logger.info(f"Pushed changes to repository")
        pull_request_input = CreatePullRequestInput(title=work_item.title, source_branch=branch_name,
                                                    description=work_item.description)
        self.ado_repos_api.create_pull_request(pull_request_input)
        loguru.logger.info(f"Created pull request for task: {work_item.title}")
        return workspace_dir


if __name__ == "__main__":
    TaskAutomation().listen_and_process_tasks()
