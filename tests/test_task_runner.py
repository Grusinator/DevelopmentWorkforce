import os
from random import randint
from unittest.mock import patch
from pathlib import Path
import pytest

from development_workforce.ado_integrations.workitems.ado_workitem_models import AdoWorkItem
from development_workforce.ado_integrations.workitems.mock_ado_workitems_api import MockAdoWorkitemsApi
from development_workforce.task_listener import TaskAutomation



work_item = AdoWorkItem(
        id=randint(1, 99999),
        title="Test Task",
        description="This is a test task",
        assigned_to="William Sandvej Hansen",
        state="New"
    )


# Mock for the AI runner that writes a dummy file
def mock_ai_runner(description, workspace_dir):
    dummy_file_path = workspace_dir / "dummy_file.txt"
    with dummy_file_path.open("w") as dummy_file:
        dummy_file.write(f"This is a dummy file created by the mocked AI runner:  \n{description}")


@pytest.fixture
def task_automation_setup():
    with patch('development_workforce.task_listener.CrewTaskRunner.run', side_effect=mock_ai_runner), \
            patch('development_workforce.task_listener.ADOReposWrapperApi.create_pull_request',
                  return_value="MockPR123"):
        task_automation = TaskAutomation()
        api = MockAdoWorkitemsApi()
        api.work_items = [work_item]
        task_automation.ado_workitems_api = api
        yield task_automation


def test_task_automation_process(task_automation_setup):
    workspace_dir = task_automation_setup.find_new_task()
    assert workspace_dir.exists()
    dummy_file_path = workspace_dir / "dummy_file.txt"
    assert dummy_file_path.exists()


