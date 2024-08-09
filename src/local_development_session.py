import textwrap
from pathlib import Path
from typing import List

import loguru

from src.crew.crew_task_runner import CrewTaskRunner
from src.crew.models import LocalDevelopmentResult
from src.devops_integrations.pull_requests.pull_request_models import PullRequestCommentThreadModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.models import TaskExtraInfo
from src.util_tools.map_dir import DirectoryStructure
from src.util_tools.vector_db import VectorDB


class LocalDevelopmentSession:

    def local_development_on_workitem(self, work_item: WorkItemModel, repo_dir: Path,
                                      task_extra_info: TaskExtraInfo = None) -> LocalDevelopmentResult:
        loguru.logger.info(f"Processing task: {work_item.title}")
        result = self._run_development_crew(work_item, repo_dir, task_extra_info)
        loguru.logger.info(f"Completed task: {work_item.title}")
        self.run_post_ai_checks()
        loguru.logger.info("Pushed changes to repository")

        return result

    def _run_development_crew(self, work_item, repo_dir, task_extra_info) -> LocalDevelopmentResult:
        task_context = self.prepare_task_context(work_item, repo_dir, task_extra_info)
        crew_runner = CrewTaskRunner(repo_dir)
        crew_runner.add_developer_agent()
        [crew_runner.add_task_handle_comment_thread(thread, work_item) for thread in task_extra_info.pr_comments or []]
        crew_runner.add_task_from_work_item(work_item, extra_info=task_context)
        result = crew_runner.run()
        return result

    def create_pr_comments_text(self, pr_comment_threads: List[PullRequestCommentThreadModel]):
        join = "\n".join([self.format_thread(thread) for thread in pr_comment_threads])
        return "Comments from pr:" + join if len(pr_comment_threads) else ""

    def load_most_relevant_docs_from_repo(self, work_item: WorkItemModel, repo_dir):
        vdb = VectorDB()
        vdb.load_repo(repo_dir)
        frac_of_repo = int(5 + len(vdb.filenames) / 20)
        docs = vdb.fetch_most_relevant_docs(work_item.pretty_print(), n=max(10, frac_of_repo))
        files_joined = vdb.format_files_as_text(docs)
        return files_joined

    def prepare_task_context(self, work_item, repo_dir, task_extra_info: TaskExtraInfo) -> str:
        files_as_text = self.load_most_relevant_docs_from_repo(work_item, repo_dir)
        directory_structure = DirectoryStructure(repo_dir).get_formatted_directory_structure()
        comments_from_pr = self.create_pr_comments_text(task_extra_info.pr_comments)
        dir_structure_text = f"""
        structure of workspace folder:
        {directory_structure}

        {comments_from_pr}
        
        """
        # This is a subset of existing files in the repo, in order to give some context for the development task:
        #
        # {files_as_text}

        return textwrap.dedent(dir_structure_text).lstrip()

    def run_post_ai_checks(self):
        pass

    def format_thread(self, thread: PullRequestCommentThreadModel):
        return "\n".join([comment.text for comment in thread.comments])
