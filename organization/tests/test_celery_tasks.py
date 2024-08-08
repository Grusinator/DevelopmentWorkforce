from unittest.mock import patch

import pytest
from celery.result import EagerResult
from django.db import connections

from organization.schemas import AgentModel
from organization.tasks import execute_task_workitem
from organization.tasks import fetch_new_tasks_periodically
from src.devops_integrations.repos.ado_repos_models import RepositoryModel


@pytest.mark.django_db
class TestCeleryTasks:

    def test_fetch_new_tasks_periodically(self, repo_in_db, agent_in_db):
        fetch_new_tasks_periodically(mock=True)

    @patch('organization.tasks.TaskAutomation', autospec=True)
    def test_execute_task(self, mock_task_automation, agent_in_db, repo_in_db, work_item_model):
        mock_task_automation_instance = mock_task_automation.return_value
        agent = AgentModel.model_validate(agent_in_db).model_dump()
        repo = RepositoryModel.model_validate(repo_in_db).model_dump()
        work_item = work_item_model.model_dump()
        execute_task_workitem(agent, repo, work_item, mock=True)
        mock_task_automation.assert_called_once()
        mock_task_automation_instance.develop_on_task.assert_called_once()

    @pytest.mark.skip(
        "implement this to test the issue, celery_worker fixture removed due to: (unicode error) 'unicodeescape' cod")
    @pytest.mark.django_db
    def test_execute_task_workitem(self, agent_in_db, repository, work_item_model):
        agent_md = AgentModel.model_validate(agent_in_db)
        repo_md = RepositoryModel.model_validate(repository)
        work_item_md = work_item_model

        for conn in connections.all():
            conn.close()

        result = execute_task_workitem.apply_async(
            args=[agent_md.model_dump(), repo_md.model_dump(), work_item_md.model_dump()])

        assert isinstance(result, EagerResult)  # Check if result is eager (synchronous)
        assert result.status == "SUCCESS"
