from unittest.mock import Mock
from unittest.mock import patch

import pytest

from organization.models import AgentTask
from organization.services.task_fetcher_and_scheduler import TaskFetcherAndScheduler, EXECUTE_TASK_WORKITEM_NAME
from src.crew.models import AutomatedTaskResult
from src.devops_integrations.workitems.ado_workitem_models import WorkItemStateEnum
from src.task_automation import TaskAutomation


class TestTaskFetcherAndScheduler:

    @pytest.mark.parametrize(
        "state, should_schedule",
        [
            (WorkItemStateEnum.PENDING, True),
            (WorkItemStateEnum.IN_PROGRESS, False),
            (WorkItemStateEnum.COMPLETED, False),
            (WorkItemStateEnum.FAILED, False),
        ]
    )
    def test_fetch_new_workitems_gets_scheduled(self, fetcher_and_scheduler, agent_model, repository_model,
                                                work_item_model,
                                                state, should_schedule):
        fetcher_and_scheduler.celery_worker = Mock()
        work_item_model.state = state
        fetcher_and_scheduler.fetch_new_workitems(agent_model, repository_model)
        args = [agent_model.model_dump(), repository_model.model_dump(), work_item_model.model_dump()]
        if should_schedule:
            fetcher_and_scheduler.celery_worker.schedule_task.assert_called_once_with(EXECUTE_TASK_WORKITEM_NAME, "1",
                                                                                      *args)
        else:
            fetcher_and_scheduler.celery_worker.schedule_task.assert_not_called()

    def test_fetch_pull_requests_waiting_for_author_gets_scheduled(self, fetcher_and_scheduler, agent_model,
                                                                   repository_model,
                                                                   pull_request_model, work_item_model):
        fetcher_and_scheduler.celery_worker = Mock()
        fetcher_and_scheduler.get_work_item_related_to_pr = Mock(return_value=work_item_model)
        fetcher_and_scheduler.repos_api.repositories.append(repository_model)
        fetcher_and_scheduler.pull_requests_api.pull_requests.append(pull_request_model)
        pull_requests = fetcher_and_scheduler.fetch_pull_requests_waiting_for_author(agent_model, repository_model)
        args = [agent_model.model_dump(), repository_model.model_dump(), pull_request_model.model_dump(),
                work_item_model.model_dump()]
        fetcher_and_scheduler.celery_worker.schedule_task.assert_called_once_with('execute_task_pr_feedback', "1",
                                                                                  *args)
        assert isinstance(pull_requests, list)
        for pr in pull_requests:
            assert pr.status == "active"
            assert pr.repository.source_id == repository_model.source_id
            assert pr.created_by_name == agent_model.agent_user_name
            assert pr.repository.git_url is not None

    def test_task_registration(self, fetcher_and_scheduler: TaskFetcherAndScheduler, agent_model, work_item_model):
        tasks = fetcher_and_scheduler.celery_worker.app.tasks
        assert 'execute_task_workitem' in tasks
        assert 'execute_task_pr_feedback' in tasks
        assert fetcher_and_scheduler.celery_worker.app.main == "test"

    @patch.object(TaskAutomation, 'develop_on_task')
    def test_handle_task_completion_called(self, mock_develop_on_task, fetcher_and_scheduler, agent_model,
                                           repository_model, work_item_model):
        fetcher_and_scheduler._handle_task_completion = Mock()
        mock_develop_on_task.return_value = AutomatedTaskResult(succeeded=True, token_usage=42, task_results=[])
        fetcher_and_scheduler.schedule_workitem_task(agent_model, repository_model, work_item_model)
        agent_task = AgentTask.objects.get(work_item__source_id=work_item_model.source_id)
        assert fetcher_and_scheduler._handle_task_completion.called_once(agent_task)

    @patch.object(TaskAutomation, 'develop_on_task')
    def test_task_execution_and_signal_handling(self, mock_develop_on_task, fetcher_and_scheduler, agent_model,
                                                repository_model, work_item_model):
        mock_develop_on_task.return_value = AutomatedTaskResult(succeeded=True, token_usage=42, task_results=[],
                                                                pr_id=123)
        result = fetcher_and_scheduler.schedule_workitem_task(agent_model, repository_model, work_item_model)
        result.get()
        agent_task = AgentTask.objects.get(work_item__source_id=work_item_model.source_id)
        assert agent_task.token_usage == 42
        assert agent_task.work_item.state == WorkItemStateEnum.COMPLETED
        assert agent_task.work_item.pull_request_source_id == '123'

    @patch.object(TaskAutomation, 'update_pr_from_feedback')
    def test_task_execution_pr_feedback(self, mock_update_pr_from_feedback, fetcher_and_scheduler, agent_model,
                                        repository_model, work_item_model, pull_request_model):
        # Mock the TaskAutomation.update_pr_from_feedback to return a successful LocalDevelopmentResult
        mock_update_pr_from_feedback.return_value = AutomatedTaskResult(succeeded=True, token_usage=10,
                                                                        task_results=[])

        # Schedule a PR feedback task and run it
        fetcher_and_scheduler.schedule_pr_feedback_task(agent_model, repository_model, pull_request_model,
                                                        work_item_model)

        # Verify that the AgentTask and WorkItem have been updated in the database
        agent_task = AgentTask.objects.get(work_item__source_id=work_item_model.source_id)
        assert agent_task.token_usage == 10
        assert agent_task.work_item.state == WorkItemStateEnum.COMPLETED

    @pytest.mark.skip
    @patch.object(TaskAutomation, 'develop_on_task')
    @patch.object(TaskFetcherAndScheduler, '_handle_task_completion')
    @patch.object(TaskFetcherAndScheduler, '_handle_task_picked_up')
    def test_task_lifecycle_and_agent_task_updates(self, mock_handle_task_picked_up, mock_handle_task_completion,
                                                   mock_develop_on_task, fetcher_and_scheduler, agent_model,
                                                   repository_model, work_item_model):
        # Mock the develop_on_task to return a successful AutomatedTaskResult
        mock_develop_on_task.return_value = AutomatedTaskResult(succeeded=True, token_usage=50, task_results=[])

        # Schedule and run the task
        result = fetcher_and_scheduler.schedule_workitem_task(agent_model, repository_model, work_item_model)

        # Verify that _handle_task_picked_up was called before the work started
        mock_handle_task_picked_up.assert_called_once()

        # Ensure _handle_task_completion hasn't been called yet
        mock_handle_task_completion.assert_not_called()

        # Wait for the task to complete
        result.get()

        # Verify that _handle_task_completion was called after the work finished
        mock_handle_task_completion.assert_called_once()

        # Get the AgentTask object
        agent_task = AgentTask.objects.get(work_item__source_id=work_item_model.source_id)

        # Verify that the AgentTask object was updated
        assert agent_task.token_usage == 50
        assert agent_task.work_item.state == WorkItemStateEnum.COMPLETED

        # Verify the order of calls
        assert mock_handle_task_picked_up.call_count == 1
        assert mock_develop_on_task.call_count == 1
        assert mock_handle_task_completion.call_count == 1
        assert mock_handle_task_picked_up.call_args[0][0].work_item.source_id == work_item_model.source_id
        assert mock_handle_task_completion.call_args[0][0].work_item.source_id == work_item_model.source_id
