from unittest.mock import MagicMock

import pytest

from organization.services.job_scheduler.eager_job_scheduler import EagerJobScheduler
from src.crew.models import AutomatedTaskResult
from src.job_runner.work_item_task import ExecuteTaskWorkItemHandler, ExecuteTaskWorkItemInputModel


class TestEagerJobScheduler:


    @pytest.mark.asyncio
    async def test_schedule_workitem_job(self, repository_model, agent_model, work_item_model):
        scheduler = EagerJobScheduler()
        scheduler.runner.task_handlers[0]._execute = MagicMock(return_value=AutomatedTaskResult(succeeded=True))
        input_model = ExecuteTaskWorkItemInputModel(agent=agent_model, repo=repository_model, work_item=work_item_model)
        scheduler.schedule_job(ExecuteTaskWorkItemHandler.name, "testid", input_model)
        result = await scheduler.get_job_result("testid")
        assert result.succeeded == True
