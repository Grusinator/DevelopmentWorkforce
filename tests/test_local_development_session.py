import io
from unittest.mock import MagicMock

import pytest

from src.devops_integrations.pull_requests.pull_request_models import PullRequestCommentThreadModel, \
    PullRequestCommentModel
from src.local_development_session import LocalDevelopmentSession, TaskExtraInfo
from src.util_tools.map_dir import DirectoryStructure
from tests.conftest import run_pytest_in_workspace, SimpleWorkItemModel


class TestLocalDevelopmentSession:

    @pytest.mark.requires_llm
    @pytest.mark.parametrize("work_item_description", [
        # "Python function that calculates the factorial of a given number so that I can use it for mathematical computations.",
        "add a method to the api class that can fetch pokemon moves from api, and test if you can get charizard moves",
    ])
    def test_run_task_locally(self, workspace_dir_dummy_repo, work_item_description, mock_repository):
        session = LocalDevelopmentSession()
        work_item = SimpleWorkItemModel(description=work_item_description)
        result = session.local_development_on_workitem(work_item, workspace_dir_dummy_repo)
        assert result.succeeded
        run_pytest_in_workspace(workspace_dir_dummy_repo)
        struct = DirectoryStructure(workspace_dir_dummy_repo).get_formatted_directory_structure()
        print(struct)

    def test_build_task_context(self, workspace_dir_dummy_repo, mock_work_item, file_regression):
        extra_info = TaskExtraInfo(
            pr_comments=[
                PullRequestCommentThreadModel(
                    id=1,
                    comments=[
                        PullRequestCommentModel(
                            id=1,
                            created_by="test_user",
                            created_date="2021-10-10",
                            text="This is a comment"
                        )
                    ]
                )
            ]
        )
        session = LocalDevelopmentSession()
        context = session.prepare_task_context(mock_work_item, workspace_dir_dummy_repo, extra_info)
