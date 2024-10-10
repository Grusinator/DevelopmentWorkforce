import uuid

import pytest

from organization.services.job_scheduler.kubernetes_job_scheduler import KubernetesJobScheduler
from src.job_runner.dummy_task import DummyTaskInputModel
from kubernetes import config

@pytest.mark.asyncio
async def test_kub():
    scheduler = KubernetesJobScheduler()
    config.load_kube_config(context="docker-desktop")
    job_id = str(uuid.uuid4())
    input_model = DummyTaskInputModel(string="hello")
    scheduler.schedule_job("dummy_task", job_id, input_model)
    result = await scheduler.get_job_result(job_id)
    assert result.succeeded