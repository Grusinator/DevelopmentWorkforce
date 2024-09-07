import json
import os
import sys

from kubernetes import config, client
from loguru import logger

from src.crew.models import AutomatedTaskResult
from src.job_runner.base_job_runner import BaseJobRunner


class KubernetesJobRunner(BaseJobRunner):
    def store_result(self, job_id, result: AutomatedTaskResult):
        config.load_incluster_config()
        v1 = client.CoreV1Api()


        result_data = {
            'task_id': job_id,
            'result': result.model_dump()
        }

        config_map = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(name=f"result-{job_id}"),
            data={"result": json.dumps(result_data)}
        )

        v1.create_namespaced_config_map(namespace="default", body=config_map)

    def run(self):
        job_name = os.getenv('JOB_NAME')
        job_id = os.environ.get('JOB_ID')
        encoded_args = os.getenv('ENCODED_ARGS')

        if not job_name or not encoded_args:
            logger.error("JOB_NAME and ENCODED_ARGS environment variables must be set")
            sys.exit(1)

        try:
            result = self.run_job(job_name, job_id, encoded_args)
            logger.info(f"Job {job_name} completed successfully with result: {result}")
        except Exception as e:
            logger.error(f"Job {job_name} failed with error: {e}")
            sys.exit(1)
