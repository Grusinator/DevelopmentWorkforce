from unittest.mock import patch

from organization.services.fetch_new_tasks import TaskFetcherAndScheduler
from src.devops_integrations.models import DevOpsSource
from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel, ReviewerModel


class TestFetch:
    def test_fetch_new_workitems(self, work_item_fetcher, mock_agent, get_repository, mock_work_item):
        with patch('organization.services.fetch_new_tasks.app.send_task') as mock_send_task:
            work_item_fetcher.fetch_new_workitems(mock_agent, get_repository)
            mock_send_task.assert_called_once_with(
                'organization.tasks.execute_task_workitem',
                args=[mock_agent.model_dump(), get_repository.model_dump(), mock_work_item.model_dump()]
            )

    def test_fetch_pull_requests_waiting_for_author(self, mock_agent, get_repository):
        pull_request = PullRequestModel(
            id=1,
            title="test",
            source_branch="feature",
            target_branch="main",
            status="active",
            repository=get_repository,
            reviewers=[ReviewerModel(
                source_id="test",
                display_name="",
                vote=-5
            )]
        )

        work_item_fetcher = TaskFetcherAndScheduler(mock_agent, get_repository, devops_source=DevOpsSource.MOCK)
        work_item_fetcher.pull_requests_api.pull_requests[1] = pull_request
        pull_requests = work_item_fetcher.fetch_pull_requests_waiting_for_author(mock_agent, get_repository)

        assert isinstance(pull_requests, list)
        for pr in pull_requests:
            assert pr.status == "Waiting for Author"
            assert pr.repository_id == get_repository.source_id
            assert pr.created_by == mock_agent.agent_user_name
