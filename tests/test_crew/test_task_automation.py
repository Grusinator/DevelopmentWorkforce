import os
from random import randint
from unittest.mock import patch

import pytest

from organization.schemas import AgentModel
from src.ado_integrations.repos.ado_repos_models import RepositoryModel, ProjectModel
from src.ado_integrations.workitems.ado_workitem_models import WorkItem
from src.ado_integrations.workitems.mock_ado_workitems_api import MockAdoWorkitemsApi
from src.task_automation import TaskAutomation
from src.util_tools.map_dir import DirectoryStructure
from tests.conftest import SimpleWorkItem, run_pytest_in_workspace


@pytest.fixture
def mock_work_item():
    work_item = WorkItem(
        source_id=randint(1, 99999),
        title="Test Task",
        description="This is a test task",
        assigned_to="William Sandvej Hansen",
        state="New",
        type="User Story"
    )
    return work_item


# Mock for the AI runner that writes a dummy file
@pytest.fixture
def agent_model():
    ado_org_name = os.getenv("ADO_ORGANIZATION_NAME")
    pat = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
    user_name = os.getenv("AI_USER_NAME")

    return AgentModel(id=1, organization_name=ado_org_name, pat=pat, agent_user_name=user_name, status="idle")


def mock_ai_runner(work_item: WorkItem, workspace_dir, task_context=None):
    dummy_file_path = workspace_dir / "dummy_file.txt"
    with dummy_file_path.open("w") as dummy_file:
        fil_content = f"This is a dummy file created by the mocked AI runner:  \n{work_item.description} \n\n"
        dummy_file.write(fil_content)


@pytest.fixture
def repository_model():
    repo_url = os.getenv("ADO_REPO_URL")
    repo_name = os.getenv("ADO_REPO_NAME")

    project_model = ProjectModel(id=2, name="test", source_id="test")
    return RepositoryModel(id=2, source_id="test", name=repo_name, git_url=repo_url, project=project_model)


@pytest.fixture
def task_automation_setup(mock_work_item, agent_model, repository_model):
    with patch('src.task_automation.TaskAutomation.run_development_crew', side_effect=mock_ai_runner), \
            patch('src.task_automation.ADOReposWrapperApi.create_pull_request',
                  return_value="MockPR123"):
        task_automation = TaskAutomation(repository_model, agent_model)
        api = MockAdoWorkitemsApi()
        api.work_items = [mock_work_item]
        task_automation.ado_workitems_api = api
        yield task_automation


def test_task_automation_process(task_automation_setup, mock_work_item):
    workspace_dir = task_automation_setup.process_task(mock_work_item)
    assert workspace_dir.exists()
    dummy_file_path = workspace_dir / "dummy_file.txt"
    assert dummy_file_path.exists()
    print(task_automation_setup.run_development_crew.call_args)


def test_pytest_parses_dummy_repo(workspace_dir_dummy_repo):
    run_pytest_in_workspace(workspace_dir_dummy_repo)
    struct = DirectoryStructure(workspace_dir_dummy_repo).get_formatted_directory_structure()
    print(struct)


@pytest.mark.requires_llm
@pytest.mark.parametrize("work_item_description", [
    # "Python function that calculates the factorial of a given number so that I can use it for mathematical computations.",
    "add a method to the api class that can fetch pokemon moves from api, and test if you can get charizard moves",
])
def test_run_task_locally(workspace_dir_dummy_repo, work_item_description, agent_model, repository_model):
    auto = TaskAutomation(repository_model, agent_model)
    work_item = SimpleWorkItem(description=work_item_description)
    result = auto.run_development_crew(work_item, workspace_dir_dummy_repo)

    assert "SUCCEEDED" in result

    run_pytest_in_workspace(workspace_dir_dummy_repo)
    struct = DirectoryStructure(workspace_dir_dummy_repo).get_formatted_directory_structure()
    print(struct)
