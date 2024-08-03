from unittest.mock import patch

import pytest

from organization.schemas import AgentModel
from organization.tasks import fetch_new_tasks_periodically, execute_task_workitem
from src.devops_integrations.repos.ado_repos_models import RepositoryModel


@pytest.mark.django_db
class TestCeleryTasks:

    def test_fetch_new_tasks_periodically(self, repo_in_db, agent_in_db):
        fetch_new_tasks_periodically(mock=True)

    @patch('organization.tasks.TaskAutomation', autospec=True)
    def test_execute_task(self, mock_task_automation, agent_in_db, repo_in_db, mock_work_item):
        mock_task_automation_instance = mock_task_automation.return_value
        agent = AgentModel.model_validate(agent_in_db).model_dump()
        repo = RepositoryModel.model_validate(repo_in_db).model_dump()
        work_item = mock_work_item.model_dump()
        execute_task_workitem(agent, repo, work_item, mock=True)
        mock_task_automation.assert_called_once()
        mock_task_automation_instance.develop_on_task.assert_called_once()


