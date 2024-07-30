from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.ado_integrations.repos.mock_repos_api import MockRepoApi
from src.ado_integrations.workitems.mock_ado_workitems_api import MockAdoWorkitemsApi
from src.local_development_session import LocalDevelopmentResult
from src.task_automation import TaskAutomation
from src.util_tools.map_dir import DirectoryStructure
from tests.conftest import run_pytest_in_workspace, mock_work_item, mock_agent, mock_repository


class MockDevSession:

    def __init__(self, repo_dir):
        self.repo_dir = Path(repo_dir)

    def local_development_on_workitem(self, repo, work_item):
        dummy_file_path = self.repo_dir / "dummy_file.txt"
        with dummy_file_path.open("w") as dummy_file:
            fil_content = f"This is a dummy file created by the mocked AI runner:  \n{work_item.description} \n\n"
            dummy_file.write(fil_content)
        return LocalDevelopmentResult(branch_name="DummyBranch", repo_dir=self.repo_dir, succeeded=True)


@pytest.fixture
def mocked_task_automation(mock_work_item, mock_agent, mock_repository, workspace_dir):
    task_automation = TaskAutomation(mock_repository, mock_agent)
    task_automation.ado_workitems_api = MockAdoWorkitemsApi([mock_work_item])
    task_automation.ado_repos_api = MockRepoApi()
    task_automation.ado_workitem_comments_api = MagicMock()
    task_automation.git_manager = MagicMock()
    task_automation.dev_session = MockDevSession(repo_dir=workspace_dir)
    yield task_automation


class TestTaskAutomation:
    def test_task_automation_process(self, mocked_task_automation, mock_work_item, mock_repository, workspace_dir):
        mocked_task_automation.develop_on_task(mock_work_item, mock_repository)
        dummy_file_path = workspace_dir / "dummy_file.txt"
        assert dummy_file_path.exists()
        mocked_task_automation.ado_repos_api.create_pull_request.assert_called_once()

    def test_pytest_parses_dummy_repo(self, workspace_dir_dummy_repo):
        run_pytest_in_workspace(workspace_dir_dummy_repo)
        struct = DirectoryStructure(workspace_dir_dummy_repo).get_formatted_directory_structure()
        print(struct)

