import uuid

import pytest
from kubernetes import config

from organization.services.job_scheduler.kubernetes_job_scheduler import KubernetesJobScheduler
from src.job_runner.dummy_task import DummyTaskInputModel
from src.job_runner.work_item_task import ExecuteTaskWorkItemHandler, ExecuteTaskWorkItemInputModel


class TestKubernetesTaskScheduler:

    @pytest.mark.asyncio
    async def test_dummy_task(self):
        scheduler = KubernetesJobScheduler()
        config.load_kube_config(context="docker-desktop")
        job_id = str(uuid.uuid4())
        input_model = DummyTaskInputModel(string="hello")
        scheduler.schedule_job("dummy_task", job_id, input_model)
        result = await scheduler.get_job_result(job_id, timeout=20)
        assert result.succeeded

    @pytest.mark.requires_lmm
    @pytest.mark.asyncio
    async def test_run_task_on_kubernetes(self, agent_model, get_repository, create_work_item):
        scheduler = KubernetesJobScheduler()
        input_model = ExecuteTaskWorkItemInputModel(agent=agent_model, repo=get_repository, work_item=create_work_item)
        job_id = str(uuid.uuid4())
        scheduler.schedule_job(ExecuteTaskWorkItemHandler.name, job_id, input_model)
        res = await scheduler.get_job_result(job_id, timeout=600)
        assert res.error_message == None
        assert res.succeeded == True
