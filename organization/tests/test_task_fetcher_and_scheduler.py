from unittest.mock import Mock
from unittest.mock import patch

import pytest

from organization.models import AgentTask
from organization.services.task_fetcher_and_scheduler import TaskFetcherAndScheduler
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
        fetcher_and_scheduler.job_scheduler = Mock()
        work_item_model.state = state
        fetcher_and_scheduler.fetch_new_workitems(agent_model, repository_model)
        args = [agent_model.model_dump(), repository_model.model_dump(), work_item_model.model_dump()]
        if should_schedule:
            fetcher_and_scheduler.job_scheduler.schedule_job.assert_called_once_with("some work item name", "1",
                                                                                      *args)
        else:
            fetcher_and_scheduler.job_scheduler.schedule_job.assert_not_called()

    def test_fetch_pull_requests_waiting_for_author_gets_scheduled(self, fetcher_and_scheduler, agent_in_db, agent_model,
                                                                   repository_model,
                                                                   pull_request_model, work_item_model):
        fetcher_and_scheduler.job_scheduler = Mock()
        fetcher_and_scheduler.get_work_item_related_to_pr = Mock(return_value=work_item_model)
        fetcher_and_scheduler.repos_api.repositories.append(repository_model)
        fetcher_and_scheduler.pull_requests_api.pull_requests.append(pull_request_model)
        pull_requests = fetcher_and_scheduler.fetch_pull_requests_waiting_for_author(agent_model, repository_model)
        args = [agent_model.model_dump(), repository_model.model_dump(), pull_request_model.model_dump(),
                work_item_model.model_dump()]
        task_id = str(AgentTask.objects.get(work_item__source_id=work_item_model.source_id).id)
        fetcher_and_scheduler.job_scheduler.schedule_job.assert_called_once_with('execute_task_pr_feedback', task_id,
                                                                                  *args)
        assert isinstance(pull_requests, list)
        for pr in pull_requests:
            assert pr.status == "active"
            assert pr.repository.source_id == repository_model.source_id
            assert pr.created_by_name == agent_model.agent_user_name
            assert pr.repository.git_url is not None




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
