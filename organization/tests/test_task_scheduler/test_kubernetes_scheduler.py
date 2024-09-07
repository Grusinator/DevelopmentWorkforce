from organization.services.job_scheduler.kubernetes_job_scheduler import KubernetesJobScheduler


class TestKubernetesTaskScheduler:
    def test_run_task_on_kubernetes(self):
        scheduler = KubernetesJobScheduler()
        scheduler.core_v1.read_namespaced_config_map