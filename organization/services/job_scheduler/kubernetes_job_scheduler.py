import asyncio
import os

from kubernetes import client, config
from kubernetes.client import ApiException
from loguru import logger
from pydantic import BaseModel

from organization.services.job_scheduler.base_job_scheduler import BaseJobScheduler
from src.crew.models import AutomatedTaskResult


class ConfigMapResultModel(BaseModel):
    task_id: str
    result: AutomatedTaskResult


from kubernetes import client, config
from kubernetes.client import ApiException
from loguru import logger


class KubernetesJobScheduler:
    namespace = "default"

    def __init__(self):
        config.load_kube_config()
        self.batch_v1 = client.BatchV1Api()
        self.core_v1 = client.CoreV1Api()
        self.create_namespace()
        self.create_configmap_rbac()

    def create_namespace(self):
        try:
            # Create the namespace if it does not exist
            self.core_v1.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=self.namespace)))
            logger.info(f"Namespace {self.namespace} created.")
        except ApiException as e:
            if e.status == 409:  # Namespace already exists
                logger.info(f"Namespace {self.namespace} already exists.")
            else:
                raise

    def create_configmap_rbac(self):
        rbac_api = client.RbacAuthorizationV1Api()

        # Define the Role for ConfigMap permissions in the specific namespace
        role = client.V1Role(
            metadata=client.V1ObjectMeta(name="configmap-role", namespace=self.namespace),
            rules=[
                client.V1PolicyRule(
                    api_groups=[""],
                    resources=["configmaps"],
                    verbs=["create", "update", "delete", "get", "list", "watch"]
                )
            ]
        )

        # Define the RoleBinding for the ServiceAccount
        role_binding = client.V1RoleBinding(
            metadata=client.V1ObjectMeta(name="configmap-rolebinding", namespace=self.namespace),
            role_ref=client.V1RoleRef(
                api_group="rbac.authorization.k8s.io",
                kind="Role",
                name="configmap-role"
            ),
            subjects=[
                client.models.RbacV1Subject(
                    kind="ServiceAccount",
                    name="default",  # Use the 'default' service account in the namespace
                    namespace=self.namespace
                )
            ]
        )

        try:
            # Create the Role
            rbac_api.create_namespaced_role(namespace=self.namespace, body=role)
            logger.info(f"Role 'configmap-role' created in namespace {self.namespace}.")
        except ApiException as e:
            if e.status == 409:  # Role already exists
                logger.info(f"Role 'configmap-role' already exists in namespace {self.namespace}.")
            else:
                raise

        try:
            # Create the RoleBinding
            rbac_api.create_namespaced_role_binding(namespace=self.namespace, body=role_binding)
            logger.info(f"RoleBinding 'configmap-rolebinding' created in namespace {self.namespace}.")
        except ApiException as e:
            if e.status == 409:  # RoleBinding already exists
                logger.info(f"RoleBinding 'configmap-rolebinding' already exists in namespace {self.namespace}.")
            else:
                raise

    def schedule_job(self, job_name: str, job_id: str, input_model: BaseModel) -> str:
        input_model_json = input_model.model_dump_json()

        job = client.V1Job(
            metadata=client.V1ObjectMeta(name=f"{job_name.replace('_', '-')}-{job_id}"),
            spec=client.V1JobSpec(
                backoff_limit=0,
                template=client.V1PodTemplateSpec(
                    spec=client.V1PodSpec(
                        restart_policy="Never",
                        containers=[
                            client.V1Container(
                                name="task-automation",
                                image="task-automation:latest",
                                image_pull_policy="IfNotPresent",
                                command=["python", "src/run_job.py"],
                                args=[job_name, input_model_json],
                                env=[
                                        client.V1EnvVar(name="JOB_ID", value=job_id),
                                        client.V1EnvVar(name="JOB_NAME", value=job_name),
                                        client.V1EnvVar(name="ENCODED_ARGS", value=input_model_json),
                                        client.V1EnvVar(name="WORKSPACE_DIR", value="/app/workspace"),
                                    ] + [
                                        client.V1EnvVar(name=name, value=value) for name, value in os.environ.items()
                                        if name in ["OPENAI_MODEL_NAME", "OPENAI_API_KEY", ]
                                    ],
                            )
                        ]
                    )
                )
            )
        )

        self.batch_v1.create_namespaced_job(namespace=self.namespace, body=job)
        return job_id

    async def get_job_result(self, job_id: str, timeout: int = 60) -> AutomatedTaskResult:
        """
        Asynchronously waits for the job result ConfigMap to become available and retrieves it.

        :param job_id: The ID of the job.
        :param timeout: The maximum time to wait for the result in seconds.
        :return: AutomatedTaskResult instance.
        """
        config_map_name = f"job-result-{job_id}"
        end_time = asyncio.get_event_loop().time() + timeout

        while True:
            try:
                config_map = self.core_v1.read_namespaced_config_map(
                    name=config_map_name,
                    namespace=self.namespace
                )
                result_json = config_map.data["result"]
                return ConfigMapResultModel.model_validate_json(result_json).result
            except ApiException as e:
                if e.status == 404:
                    # ConfigMap not yet available
                    if asyncio.get_event_loop().time() >= end_time:
                        raise TimeoutError(f"Timed out waiting for job result ConfigMap '{config_map_name}'.")
                    await asyncio.sleep(1)  # Wait for 1 second before retrying
                else:
                    # Some other error occurred
                    raise
