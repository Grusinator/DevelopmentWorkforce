from unittest.mock import patch

from organization.services.fetch_new_tasks import TaskFetcherAndScheduler
from src.devops_integrations.models import DevOpsSource


class TestFetch:
    def test_fetch_new_workitems(self, work_item_fetcher, mock_agent, get_repository, mock_work_item):
        with patch('organization.services.fetch_new_tasks.app.send_task') as mock_send_task:
            work_item_fetcher.fetch_new_workitems(mock_agent, get_repository)
            mock_send_task.assert_called_once_with(
                'organization.tasks.execute_task',
                args=[mock_agent.model_dump(), get_repository.model_dump(), mock_work_item.model_dump()]
            )

    def test_fetch_pull_requests_waiting_for_author(self, mock_agent, get_repository):
        work_item_fetcher = TaskFetcherAndScheduler(mock_agent, get_repository, devops_source=DevOpsSource.ADO)
        pull_requests = work_item_fetcher.fetch_pull_requests_waiting_for_author(mock_agent, get_repository)

        assert isinstance(pull_requests, list)
        for pr in pull_requests:
            assert pr.status == "Waiting for Author"
            assert pr.repository_id == get_repository.source_id
            assert pr.created_by == mock_agent.agent_user_name
