from pathlib import Path
from unittest.mock import MagicMock

import pytest

from organization.models import Repository
from src.devops_integrations.models import DevOpsSource
from src.devops_integrations.repos.mock_repos_api import MockReposApi
from src.devops_integrations.workitems.ado_workitem_models import WorkItem, CreateWorkItemInput
from src.devops_integrations.workitems.mock_workitems_api import MockWorkitemsApi
from src.local_development_session import LocalDevelopmentResult
from src.task_automation import TaskAutomation
from src.util_tools.map_dir import DirectoryStructure
from tests.conftest import run_pytest_in_workspace, mock_work_item, mock_agent, mock_repository


class MockDevSession:

    def __init__(self, repo_dir):
        self.repo_dir = Path(repo_dir)

    def local_development_on_workitem(self, work_item: WorkItem, repo: Repository):
        dummy_file_path = self.repo_dir / "dummy_file.txt"
        with dummy_file_path.open("w") as dummy_file:
            fil_content = f"This is a dummy file created by the mocked AI runner:  \n{work_item.description} \n\n"
            dummy_file.write(fil_content)
        return LocalDevelopmentResult(branch_name="DummyBranch", repo_dir=self.repo_dir, succeeded=True)


@pytest.fixture
def mocked_task_automation(mock_work_item, mock_agent, mock_repository, workspace_dir):
    task_automation = TaskAutomation(mock_repository, mock_agent, devops_source=DevOpsSource.MOCK)
    task_automation.devops_factory.mock_workitems_api.work_items.append(mock_work_item)
    task_automation.git_manager = MagicMock()
    task_automation.dev_session = MockDevSession(repo_dir=workspace_dir)
    yield task_automation


class TestTaskAutomation:
    def test_task_automation_process(self, mocked_task_automation, mock_work_item, mock_repository, workspace_dir):
        mocked_task_automation.develop_on_task(mock_work_item, mock_repository)
        dummy_file_path = workspace_dir / "dummy_file.txt"
        assert dummy_file_path.exists()
        assert len(mocked_task_automation.pull_requests_api.pull_requests) == 1

    def test_pytest_parses_dummy_repo(self, workspace_dir_dummy_repo):
        run_pytest_in_workspace(workspace_dir_dummy_repo)
        struct = DirectoryStructure(workspace_dir_dummy_repo).get_formatted_directory_structure()
        print(struct)
