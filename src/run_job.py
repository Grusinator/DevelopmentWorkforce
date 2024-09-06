from src.job_runner.kubernetes_job_runner import KubernetesJobRunner

if __name__ == "__main__":
    job_runner = KubernetesJobRunner()
    job_runner.run()
