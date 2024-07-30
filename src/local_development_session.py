import os
import textwrap
import uuid
from pathlib import Path

import loguru
from pydantic import BaseModel

from src.ado_integrations.repos.ado_repos_models import RepositoryModel
from src.ado_integrations.workitems.ado_workitem_models import WorkItem
from src.crew.crew_task_runner import CrewTaskRunner
from src.git_manager import GitManager
from src.util_tools.map_dir import DirectoryStructure
from src.util_tools.vector_db import VectorDB


class LocalDevelopmentResult(BaseModel):
    succeeded: bool


class LocalDevelopmentSession:

    def local_development_on_workitem(self, work_item: WorkItem, repo_dir: Path):
        loguru.logger.info(f"Processing task: {work_item.title}")
        result = self._run_development_crew(work_item, repo_dir)
        loguru.logger.info(f"Completed task: {work_item.title}")
        self.run_post_ai_checks()
        loguru.logger.info("Pushed changes to repository")
        return LocalDevelopmentResult(succeeded=result == "SUCCEEDED")

    def _run_development_crew(self, work_item, repo_dir) -> str:
        task_context = self.prepare_task_context(work_item, repo_dir)
        crew_runner = CrewTaskRunner(repo_dir)
        crew_runner.add_developer_agent()
        crew_runner.add_task_from_work_item(work_item, extra_info=task_context)
        return crew_runner.run()

    def prepare_task_context(self, work_item, repo_dir):
        files_as_text = self.load_most_relevant_docs_from_repo(work_item, repo_dir)
        directory_structure = DirectoryStructure(repo_dir).get_formatted_directory_structure()
        dir_structure_text = f"""
        structure of workspace folder:
        {directory_structure}

        """
        # This is a subset of existing files in the repo, in order to give some context for the development task:
        #
        # {files_as_text}

        return textwrap.dedent(dir_structure_text).lstrip()

    def load_most_relevant_docs_from_repo(self, work_item: WorkItem, repo_dir):
        vdb = VectorDB()
        vdb.load_repo(repo_dir)
        frac_of_repo = int(5 + len(vdb.filenames) / 20)
        docs = vdb.fetch_most_relevant_docs(work_item.pretty_print(), n=max(10, frac_of_repo))
        files_joined = vdb.format_files_as_text(docs)
        return files_joined

    def run_post_ai_checks(self):
        pass
