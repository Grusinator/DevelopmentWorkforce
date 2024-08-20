from unittest.mock import Mock


class TestFetch:
    def test_fetch_new_workitems(self, work_item_fetcher, agent_model, get_repository, work_item_model):
        work_item_fetcher.celery_worker = Mock()
        work_item_fetcher.fetch_new_workitems(agent_model, get_repository)
        args = [agent_model.model_dump(), get_repository.model_dump(), work_item_model.model_dump()]
        work_item_fetcher.celery_worker.add_task.assert_called_once_with('execute_task_workitem', *args)

    def test_fetch_pull_requests_waiting_for_author(self, work_item_fetcher, agent_model, repository_model,
                                                    pull_request_model, work_item_model):
        work_item_fetcher.celery_worker = Mock()
        work_item_fetcher.get_work_item_related_to_pr = Mock(return_value=work_item_model)
        work_item_fetcher.repos_api.repositories.append(repository_model)
        work_item_fetcher.pull_requests_api.pull_requests.append(pull_request_model)
        pull_requests = work_item_fetcher.fetch_pull_requests_waiting_for_author(agent_model, repository_model)
        args = [agent_model.model_dump(), repository_model.model_dump(), pull_request_model.model_dump(),
                work_item_model.model_dump()]
        work_item_fetcher.celery_worker.add_task.assert_called_once_with('execute_task_pr_feedback', *args)
        assert isinstance(pull_requests, list)
        for pr in pull_requests:
            assert pr.status == "active"
            assert pr.repository.source_id == repository_model.source_id
            assert pr.created_by_name == agent_model.agent_user_name
            assert pr.repository.git_url is not None
