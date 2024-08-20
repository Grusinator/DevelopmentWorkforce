from unittest.mock import Mock
from unittest.mock import patch

from organization.models import AgentTask
from organization.services.task_fetcher_and_scheduler import TaskFetcherAndScheduler
from src.crew.models import LocalDevelopmentResult
from src.devops_integrations.pull_requests.pull_request_models import PullRequestModel
from src.task_automation import TaskAutomation


class TestFetch:
    def test_fetch_new_workitems(self, fetcher_and_scheduler, agent_model, repository_model, work_item_model):
        fetcher_and_scheduler.celery_worker = Mock()
        fetcher_and_scheduler.fetch_new_workitems(agent_model, repository_model)
        args = [agent_model.model_dump(), repository_model.model_dump(), work_item_model.model_dump()]
        fetcher_and_scheduler.celery_worker.add_task.assert_called_once_with('execute_task_workitem', *args)

    def test_fetch_pull_requests_waiting_for_author(self, fetcher_and_scheduler, agent_model, repository_model,
                                                    pull_request_model, work_item_model):
        fetcher_and_scheduler.celery_worker = Mock()
        fetcher_and_scheduler.get_work_item_related_to_pr = Mock(return_value=work_item_model)
        fetcher_and_scheduler.repos_api.repositories.append(repository_model)
        fetcher_and_scheduler.pull_requests_api.pull_requests.append(pull_request_model)
        pull_requests = fetcher_and_scheduler.fetch_pull_requests_waiting_for_author(agent_model, repository_model)
        args = [agent_model.model_dump(), repository_model.model_dump(), pull_request_model.model_dump(),
                work_item_model.model_dump()]
        fetcher_and_scheduler.celery_worker.add_task.assert_called_once_with('execute_task_pr_feedback', *args)
        assert isinstance(pull_requests, list)
        for pr in pull_requests:
            assert pr.status == "active"
            assert pr.repository.source_id == repository_model.source_id
            assert pr.created_by_name == agent_model.agent_user_name
            assert pr.repository.git_url is not None


class TestCeleryIntegration:

    def test_task_registration(self, fetcher_and_scheduler: TaskFetcherAndScheduler, agent_model, work_item_model):
        tasks = fetcher_and_scheduler.celery_worker.app.tasks
        assert 'execute_task_workitem' in tasks
        assert 'execute_task_pr_feedback' in tasks
        assert fetcher_and_scheduler.celery_worker.app.main == "test"

    @patch.object(TaskAutomation, 'develop_on_task')
    def test_handle_task_completion_called(self, mock_develop_on_task, fetcher_and_scheduler, agent_model,
                                    repository_model, work_item_model):
        fetcher_and_scheduler._handle_task_completion = Mock()
        mock_develop_on_task.return_value = LocalDevelopmentResult(succeeded=True, token_usage=42, task_results=[])
        fetcher_and_scheduler.schedule_workitem_task(agent_model, repository_model, work_item_model)
        agent_task = AgentTask.objects.get(work_item__work_item_source_id=work_item_model.source_id)
        assert fetcher_and_scheduler._handle_task_completion.called_once(agent_task)

    @patch.object(TaskAutomation, 'develop_on_task')
    def test_task_execution_and_signal_handling(self, mock_develop_on_task, fetcher_and_scheduler, agent_model,
                                                repository_model, work_item_model):
        mock_develop_on_task.return_value = LocalDevelopmentResult(succeeded=True, token_usage=42, task_results=[])
        result = fetcher_and_scheduler.schedule_workitem_task(agent_model, repository_model, work_item_model)
        result.get()
        agent_task = AgentTask.objects.get(work_item__work_item_source_id=work_item_model.source_id)
        assert agent_task.token_usage == 42
        assert agent_task.work_item.status == 'completed'

    @patch.object(TaskAutomation, 'update_pr_from_feedback')
    def test_task_execution_pr_feedback(self, mock_update_pr_from_feedback, fetcher_and_scheduler, agent_model,
                                        repo_model, work_item_model):
        # Mock the TaskAutomation.update_pr_from_feedback to return a successful LocalDevelopmentResult
        mock_update_pr_from_feedback.return_value = LocalDevelopmentResult(succeeded=True, token_usage=10,
                                                                           task_results=[])

        # Mock a PullRequestModel
        pr_model = Mock(spec=PullRequestModel, id='pr_123')

        # Schedule a PR feedback task and run it
        fetcher_and_scheduler.schedule_pr_feedback_task(agent_model, repo_model, pr_model, work_item_model)

        # Verify that the AgentTask and WorkItem have been updated in the database
        agent_task = AgentTask.objects.get(work_item__work_item_source_id=work_item_model.source_id)
        assert agent_task.status == 'completed'
        assert agent_task.token_usage == 10
        assert agent_task.work_item.status == 'completed'
import pytest
from unittest.mock import patch
from celery import Celery, signals
from celery import shared_task



# Define a simple task that we will use for testing
@shared_task(name='simple_test_task', bind=True)
def simple_test_task(self, x, y):
    return x + y

# Signal handler that logs when the task is completed
@signals.task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    print(f"Task {sender.request.id} completed with result: {result}")

def test_task_signal_handling(celery_app):
    with patch('builtins.print') as mock_print:
        # Manually register the task with the Celery app if needed
        celery_app.tasks.register(simple_test_task)

        # Call the task using send_task
        result = celery_app.send_task("simple_test_task", args=(4, 5))

        # Wait for the task to complete
        result.get()

        # Ensure the task was successful
        assert result.successful()
        assert result.result == 9

        # Verify that the signal handler was called and the correct output was logged
        mock_print.assert_any_call(f"Task {result.id} completed with result: 9")
