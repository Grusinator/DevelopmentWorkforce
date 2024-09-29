from unittest.mock import MagicMock

import pytest

from organization.services.job_scheduler.eager_job_scheduler import EagerJobScheduler
from src.crew.models import AutomatedTaskResult
from src.job_runner.work_item_task import ExecuteTaskWorkItemHandler, ExecuteTaskWorkItemInputModel


class TestEagerJobScheduler:

    def test_scheduling_job_does_not_exists(self):
        scheduler = EagerJobScheduler()
        with pytest.raises(ValueError):
            scheduler.schedule_job('test_job', '12345')

    def test_schedule_workitem_job(self, repository_model, agent_model, work_item_model):
        scheduler = EagerJobScheduler()
        scheduler.runner.task_handlers[0]._execute = MagicMock(return_value=AutomatedTaskResult(succeeded=True))
        input_model = ExecuteTaskWorkItemInputModel(agent=agent_model, repo=repository_model, work_item=work_item_model)
        scheduler.schedule_job(ExecuteTaskWorkItemHandler.name, "testid", input_model)
        result = scheduler.get_job_result("testid")
        assert result.succeeded == True
