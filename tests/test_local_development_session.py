from unittest.mock import MagicMock

import pytest

from src.local_development_session import LocalDevelopmentSession
from src.util_tools.map_dir import DirectoryStructure
from tests.conftest import run_pytest_in_workspace, SimpleWorkItem


class TestLocalDevelopmentSession:

    @pytest.mark.requires_llm
    @pytest.mark.parametrize("work_item_description", [
        # "Python function that calculates the factorial of a given number so that I can use it for mathematical computations.",
        "add a method to the api class that can fetch pokemon moves from api, and test if you can get charizard moves",
    ])
    def test_run_task_locally(self, workspace_dir_dummy_repo, work_item_description, mock_repository):
        session = LocalDevelopmentSession()
        work_item = SimpleWorkItem(description=work_item_description)
        result = session.local_development_on_workitem(work_item, workspace_dir_dummy_repo)
        assert result.succeeded
        run_pytest_in_workspace(workspace_dir_dummy_repo)
        struct = DirectoryStructure(workspace_dir_dummy_repo).get_formatted_directory_structure()
        print(struct)