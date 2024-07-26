import os
from random import randint
from unittest.mock import patch

import pytest

from organization.schemas import AgentModel
from src.ado_integrations.repos.ado_repos_models import RepositoryModel, ProjectModel
from src.ado_integrations.workitems.ado_workitem_models import WorkItem
from src.ado_integrations.workitems.mock_ado_workitems_api import MockAdoWorkitemsApi
from src.task_automation import TaskAutomation

work_item = WorkItem(
    id=randint(1, 99999),
    title="Test Task",
    description="This is a test task",
    assigned_to="William Sandvej Hansen",
    state="New",
    type="User Story"
)


# Mock for the AI runner that writes a dummy file
def mock_ai_runner(work_item: WorkItem, workspace_dir, task_context=None):
    dummy_file_path = workspace_dir / "dummy_file.txt"
    with dummy_file_path.open("w") as dummy_file:
        fil_content = f"This is a dummy file created by the mocked AI runner:  \n{work_item.description} \n\n"
        dummy_file.write(fil_content)


@pytest.fixture
def task_automation_setup():
    repo_url = os.getenv("ADO_REPO_URL")
    repo_name = os.getenv("ADO_REPO_NAME")
    pat = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
    ado_org_name = os.getenv("ADO_ORGANIZATION_NAME")

    user_name = os.getenv("AI_USER_NAME")

    project_model = ProjectModel(id=2, name="test", source_id="test")
    repository_model = RepositoryModel(id=2, source_id="test", name=repo_name, git_url=repo_url, project=project_model)

    agent_model = AgentModel(id=1, organization_name=ado_org_name, pat=pat, agent_user_name=user_name, status="idle")

    pat: str
    status: str
    organization_name: str
    agent_user_name: str

    with patch('src.task_automation.TaskAutomation.run_development_crew', side_effect=mock_ai_runner), \
            patch('src.task_automation.ADOReposWrapperApi.create_pull_request',
                  return_value="MockPR123"):
        task_automation = TaskAutomation(repository_model, agent_model)
        api = MockAdoWorkitemsApi()
        api.work_items = [work_item]
        task_automation.ado_workitems_api = api
        yield task_automation


def test_task_automation_process(task_automation_setup):
    workspace_dir = task_automation_setup.process_task(work_item)
    assert workspace_dir.exists()
    dummy_file_path = workspace_dir / "dummy_file.txt"
    assert dummy_file_path.exists()
    print(task_automation_setup.run_development_crew.call_args)
