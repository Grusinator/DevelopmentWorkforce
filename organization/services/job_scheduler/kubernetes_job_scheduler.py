import kubernetes
from kubernetes import client, config

import json
import base64
from typing import Dict, Any

from organization.services.job_scheduler.base_job_scheduler import BaseJobScheduler

class KubernetesJobScheduler(BaseJobScheduler):
    def __init__(self):
        config.load_kube_config()
        self.batch_v1 = client.BatchV1Api()
        self.core_v1 = client.CoreV1Api()

    def schedule_job(self, job_name: str, job_id: str, *args, **kwargs) -> str:
        encoded_args = self.encode_args(args, kwargs)

        job = client.V1Job(
            metadata=client.V1ObjectMeta(name=f"{job_name}-{job_id}"),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="task-automation",
                                image="task-automation:latest",
                                command=["python", "run_job.py"],
                                args=[job_name, encoded_args],
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

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        # Implement logic to retrieve job result from a ConfigMap or other storage
        try:
            config_map = self.core_v1.read_namespaced_config_map(name=f"result-{job_id}", namespace="default")
            result_json = config_map.data["result"]
            return json.loads(result_json)
        except kubernetes.client.exceptions.ApiException:
            return {"status": "pending"}

    def connect_job_completion_handler(self, handler):
        # Implement logic to watch for job completion and call the handler
        # This could involve setting up a Kubernetes watch on Jobs
        pass

    def connect_job_start_handler(self, handler):
        # Implement logic to watch for job start and call the handler
        # This could involve setting up a Kubernetes watch on Jobs
        pass
