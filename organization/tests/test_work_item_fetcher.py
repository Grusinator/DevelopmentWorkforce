from unittest.mock import patch

from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel, ReviewerModel


class TestFetch:
    @patch('organization.services.fetch_new_tasks.app.send_task')
    def test_fetch_new_workitems(self, mock_send_task, work_item_fetcher, agent_model, get_repository, work_item_model):
        work_item_fetcher.fetch_new_workitems(agent_model, get_repository)
        args = [agent_model.model_dump(), get_repository.model_dump(), work_item_model.model_dump()]
        mock_send_task.assert_called_once_with('execute_task_workitem', args=args)

    @patch('organization.services.fetch_new_tasks.app.send_task')
    def test_fetch_pull_requests_waiting_for_author(self, mock_send_task, agent_model, repository_model,
                                                    pull_request_model, work_item_fetcher):
        work_item_fetcher.repos_api.repositories.append(repository_model)
        work_item_fetcher.pull_requests_api.pull_requests.append(pull_request_model)
        pull_requests = work_item_fetcher.fetch_pull_requests_waiting_for_author(agent_model, repository_model)
        args = [agent_model.model_dump(), repository_model.model_dump(), pull_request_model.model_dump()]
        mock_send_task.assert_called_once_with('execute_task_pr_feedback', args=args)
        assert isinstance(pull_requests, list)
        for pr in pull_requests:
            assert pr.status == "active"
            assert pr.repository.source_id == repository_model.source_id
            assert pr.created_by_name == agent_model.agent_user_name
            assert pr.repository.git_url is not None
