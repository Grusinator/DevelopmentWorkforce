from unittest.mock import patch

from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel, ReviewerModel


class TestFetch:
    @patch('organization.services.fetch_new_tasks.app.send_task')
    def test_fetch_new_workitems(self, mock_send_task, work_item_fetcher, agent_model, get_repository, work_item_model):
        work_item_fetcher.fetch_new_workitems(agent_model, get_repository)
        args = [agent_model.model_dump(), get_repository.model_dump(), work_item_model.model_dump()]
        mock_send_task.assert_called_once_with('execute_task_workitem', args=args)

    @patch('organization.services.fetch_new_tasks.app.send_task')
    def test_fetch_pull_requests_waiting_for_author(self, mock_send_task, agent_model, get_repository,
                                                    work_item_fetcher):
        pull_request = PullRequestModel(
            id=1,
            title="test",
            source_branch="feature",
            created_by_name=agent_model.agent_user_name,
            target_branch="main",
            status="active",
            repository=get_repository,
            reviewers=[ReviewerModel(
                source_id="test",
                display_name="",
                vote=-5
            )]
        )

        work_item_fetcher.pull_requests_api.pull_requests[1] = pull_request
        pull_requests = work_item_fetcher.fetch_pull_requests_waiting_for_author(agent_model, get_repository)
        args = [agent_model.model_dump(), get_repository.model_dump(), pull_request.model_dump()]
        mock_send_task.assert_called_once_with('execute_task_pr_feedback', args=args)
        assert isinstance(pull_requests, list)
        for pr in pull_requests:
            assert pr.status == "active"
            assert pr.repository.source_id == get_repository.source_id
            assert pr.created_by_name == agent_model.agent_user_name
