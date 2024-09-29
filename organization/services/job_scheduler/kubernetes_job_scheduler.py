from kubernetes import client, config
from pydantic import BaseModel

from organization.services.job_scheduler.base_job_scheduler import BaseJobScheduler
from src.crew.models import AutomatedTaskResult


class KubernetesJobScheduler(BaseJobScheduler):
    def __init__(self):
        config.load_kube_config()
        self.batch_v1 = client.BatchV1Api()
        self.core_v1 = client.CoreV1Api()

    def schedule_job(self, job_name: str, job_id: str, input_model: BaseModel) -> str:
        input_model_json = input_model.model_dump_json()

        job = client.V1Job(
            metadata=client.V1ObjectMeta(name=f"{job_name.replace('_', '-')}-{job_id}"),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="task-automation",
                                image="task-automation:latest",
                                command=["python", "run_job.py"],
                                args=[job_name, input_model_json],
                                env=[
                                    client.V1EnvVar(name="JOB_ID", value=job_id),
                                ]
                            )
                        ],
                        restart_policy="Never"
                    )
                )
            )
        )

        self.batch_v1.create_namespaced_job(namespace="default", body=job)
        return job_id

    def get_job_result(self, job_id: str) -> AutomatedTaskResult:
        # Implement logic to retrieve job result from a ConfigMap or other storage
        config_map = self.core_v1.read_namespaced_config_map(name=f"result-{job_id}", namespace="default")
        result_json = config_map.data["result"]
        return AutomatedTaskResult.model_validate(result_json)

    def connect_job_completion_handler(self, handler):
        # Implement logic to watch for job completion and call the handler
        # This could involve setting up a Kubernetes watch on Jobs
        pass

    def connect_job_start_handler(self, handler):
        # Implement logic to watch for job start and call the handler
        # This could involve setting up a Kubernetes watch on Jobs
        pass
