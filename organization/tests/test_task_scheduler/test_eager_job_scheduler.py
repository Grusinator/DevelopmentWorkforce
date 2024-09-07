from unittest.mock import MagicMock

import pytest

from organization.services.job_scheduler.eager_job_scheduler import EagerJobScheduler
from src.crew.models import AutomatedTaskResult
from src.job_runner.work_item_task import ExecuteTaskWorkItemHandler


class TestEagerJobScheduler:

    def test_scheduling_job_does_not_exists(self):
        scheduler = EagerJobScheduler()
        with pytest.raises(ValueError):
            scheduler.schedule_job('test_job', '12345')

    def test_schedule_workitem_job(self, repository_model, agent_model, work_item_model):
        scheduler = EagerJobScheduler()
        scheduler.runner.task_handlers[0]._execute = MagicMock(return_value=AutomatedTaskResult(succeeded=True))
        scheduler.schedule_job(ExecuteTaskWorkItemHandler.name, "testid", agent_model, repository_model, work_item_model)
        result = scheduler.get_job_result("testid")
        assert result.succeeded == "succeeded"
