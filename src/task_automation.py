# task_automation.py
import textwrap

import loguru

from organization.schemas import AgentModel
from src.ado_integrations.repos.ado_repos_models import CreatePullRequestInput, RepositoryModel
from src.ado_integrations.repos.ado_repos_wrapper_api import ADOReposWrapperApi
from src.ado_integrations.workitems.ado_workitem_models import WorkItem, UpdateWorkItemInput
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi
from src.crew.crew_task_runner import CrewTaskRunner
from src.git_manager import GitManager
from src.util_tools.map_dir import DirectoryStructure
from src.util_tools.vector_db import VectorDB


class TaskAutomation:
    def __init__(self, repo: RepositoryModel, agent: AgentModel):
        self.ado_workitems_api = ADOWorkitemsWrapperApi(agent.pat, agent.organization_name, repo.project.name)
        self.ado_repos_api = ADOReposWrapperApi(agent.pat, agent.organization_name, repo.project.name, repo.name)
        self.git_manager = GitManager(repo.git_url)
        self.user_name = agent.agent_user_name

    def get_new_tasks(self, state="New"):
        return self.ado_workitems_api.list_work_items(assigned_to=self.user_name, state=state)

    def process_task(self, work_item: WorkItem):
        work_item_input = UpdateWorkItemInput(source_id=work_item.source_id, state="Active")
        self.ado_workitems_api.update_work_item(work_item_input)
        branch_name, workspace_dir = self.local_development_on_task(work_item)
        pull_request_input = CreatePullRequestInput(title=work_item.title, source_branch=branch_name,
                                                    description=work_item.description)
        self.ado_repos_api.create_pull_request(pull_request_input)
        loguru.logger.info(f"Created pull request for task: {work_item.title}")
        return workspace_dir

    def local_development_on_task(self, work_item):
        loguru.logger.info(f"Processing task: {work_item.title}")
        workspace_dir = self.git_manager.clone_and_setup(work_item)
        loguru.logger.info(f"Cloned repository to {workspace_dir}")
        self.run_development_crew(work_item, workspace_dir)
        loguru.logger.info(f"Completed task: {work_item.title}")
        branch_name = workspace_dir.name
        self.run_post_ai_checks()
        self.git_manager.push_changes(workspace_dir, branch_name, work_item.title)
        loguru.logger.info("Pushed changes to repository")
        return branch_name, workspace_dir

    def run_development_crew(self, work_item, workspace_dir):
        task_context = self.prepare_task_context(work_item, workspace_dir)
        crew_runner = CrewTaskRunner(workspace_dir)
        crew_runner.add_developer_agent()
        crew_runner.add_task_from_work_item(work_item, extra_info=task_context)
        return crew_runner.run()

    def prepare_task_context(self, work_item, workspace_dir):
        files_as_text = self.load_most_relevant_docs_from_repo(work_item, workspace_dir)
        directory_structure = DirectoryStructure(workspace_dir).get_formatted_directory_structure()
        dir_structure_text = f"""
        structure of workspace folder:
        {directory_structure}

        """
        # This is a subset of existing files in the repo, in order to give some context for the development task:
        #
        # {files_as_text}

        return textwrap.dedent(dir_structure_text).lstrip()

    def load_most_relevant_docs_from_repo(self, work_item: WorkItem, workspace_dir):
        vdb = VectorDB()
        vdb.load_repo(workspace_dir)
        frac_of_repo = int(5 + len(vdb.filenames) / 20)
        docs = vdb.fetch_most_relevant_docs(work_item.pretty_print(), n=max(10, frac_of_repo))
        files_as_text = [f"### {filename} ###: \n  {content}" for filename, content in docs.items()]
        return "\n-------------------------------------------\n\n".join(files_as_text)

    def run_post_ai_checks(self):
        pass

