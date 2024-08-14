from pathlib import Path

import pytest

from src.crew.models import LocalDevelopmentResult
from src.devops_integrations.pull_requests.pull_request_models import PullRequestCommentThreadModel, \
    PullRequestCommentModel
from src.local_development_session import LocalDevelopmentSession
from src.models import TaskExtraInfo
from src.util_tools.map_dir import DirectoryStructure
from tests.run_pytest_in_workspace import run_pytest_in_workspace


class TestLocalDevelopmentSession:

    @pytest.mark.requires_llm
    @pytest.mark.parametrize("work_item_description", [
        # "Python function that calculates the factorial of a given number so that I can use it for mathematical computations.",
        "add a method to the api class that can fetch pokemon moves from api, and test if you can get charizard moves",
    ])
    def test_run_task_locally(self, workspace_dir_dummy_repo, work_item_description, repository_model, work_item_model):
        session = LocalDevelopmentSession()
        work_item_model.description = work_item_description
        result = session.local_development_on_workitem(work_item_model, workspace_dir_dummy_repo)
        assert result.succeeded
        run_pytest_in_workspace(workspace_dir_dummy_repo)
        struct = DirectoryStructure(workspace_dir_dummy_repo).get_formatted_directory_structure()
        print(struct)

    def test_build_task_context(self, workspace_dir_dummy_repo, work_item_model, file_regression, comment_thread_model):
        extra_info = TaskExtraInfo(
            pr_comments=[
                comment_thread_model
            ]
        )
        session = LocalDevelopmentSession()
        context = session.prepare_task_context(work_item_model, workspace_dir_dummy_repo, extra_info)

    @pytest.mark.requires_llm
    def test_local_development_result(self, workspace_dir_dummy_repo, repository_model, work_item_model,
                                      comment_thread_model):
        session = LocalDevelopmentSession()
        work_item_model.description = "create a function that adds 2 numbers"

        comment_thread_model.comments[0].text = "this is a test comment, respond with 'UNDERSTOOD'"
        extra_info = TaskExtraInfo(pr_comments=[comment_thread_model])

        result: LocalDevelopmentResult = session.local_development_on_workitem(work_item_model,
                                                                               Path(workspace_dir_dummy_repo),
                                                                               extra_info)

        assert result.task_results[0].output == "UNDERSTOOD"
        assert result.task_results[1].output == "SUCCEEDED"
        assert result.succeeded
