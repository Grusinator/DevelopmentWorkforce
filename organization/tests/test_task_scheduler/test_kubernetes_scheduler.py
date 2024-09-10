from organization.services.job_scheduler.kubernetes_job_scheduler import KubernetesJobScheduler
from src.job_runner.work_item_task import ExecuteTaskWorkItemHandler


class TestKubernetesTaskScheduler:
    def test_run_task_on_kubernetes(self, agent_model, repository_model, work_item_model):
        scheduler = KubernetesJobScheduler()
        scheduler.schedule_job(ExecuteTaskWorkItemHandler.name, "testid", agent_model, repository_model, work_item_model)
        res = scheduler.get_job_result("testid")
        assert res.succeeded == True
