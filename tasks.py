import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from invoke import task
from redis import StrictRedis

from src.devops_integrations.models import ProjectAuthenticationModel
from src.devops_integrations.pull_requests.ado_pull_requests_api import ADOPullRequestsApi
from src.devops_integrations.repos.ado_repos_api import ADOReposApi
from src.util_tools.map_dir import DirectoryStructure
from src.util_tools.read_files import ReadFiles

docker_path = Path("devops/docker")

load_dotenv()


@task
def docker_run(ctx, env=""):
    """run docker dompose with build arg"""
    base_compose = docker_path / "docker-compose.yml"
    # env_compose = docker_path / f"docker-compose.{env}.yml"
    ctx.run(f"docker-compose -f {base_compose} up --build")


@task
def docker_compose_up(c):
    """
    Run docker-compose up with the correct file path.
    """
    c.run("docker-compose -f devops/docker/docker-compose.yml up --build")

@task
def docker_compose_down(c):
    """
    Run docker-compose down with the correct file path.
    """
    c.run("docker-compose -f devops/docker/docker-compose.yml down")



@task
def start_worker(ctx):
    ctx.run("celery -A development_workforce worker --loglevel=info -E --pool=solo")


@task
def start_beat(ctx):
    ctx.run("celery -A development_workforce beat --loglevel=info")


@task
def start_flower(ctx):
    ctx.run("celery -A development_workforce flower --port=5555")


@task
def list_directory(ctx, path="."):
    struct = DirectoryStructure(path).get_formatted_directory_structure()
    print(struct)
    return struct


@task
def format_and_lint(ctx):
    """Run Python formatting and linting with Ruff and return a report"""
    result = subprocess.run(["ruff", "check", ".", "--fix"], capture_output=True, text=True)
    report = result.stdout
    print(report)
    return report


@task
def pytest_no_llm(ctx):
    """Run pytest excluding tests marked with requires_llm"""
    ctx.run('pytest -m "not requires_llm"')


@task
def read_files(ctx, *relative_dirs):
    """read multiple files at once given as space divided args like: src/file1.py src/file2.py"""
    reader = ReadFiles(Path.cwd())
    formatted_text = reader.read_and_format_files(list(relative_dirs))
    print(formatted_text)
    return formatted_text


@task
def reset_redis_messages(ctx):
    """
    Reset Redis messages by flushing all data.
    """
    redis_client = StrictRedis(host='localhost', port=6379, db=0)
    redis_client.flushall()
    print("Redis messages have been reset.")

@task
def abandon_all_prs(ctx, repo_name=None):
    auth_context = ProjectAuthenticationModel(
        pat=os.getenv("ADO_PERSONAL_ACCESS_TOKEN"),
        ado_org_name=os.getenv("ADO_ORGANIZATION_NAME"),
        project_name=os.getenv("ADO_PROJECT_NAME")
    )
    repo_name = repo_name or os.getenv("ADO_REPO_NAME")
    repository_id = ADOReposApi(auth_context).get_repository_id(repo_name)
    ado_pull_requests_api = ADOPullRequestsApi(auth_context)
    prs = ado_pull_requests_api.list_pull_requests(repository_id=repository_id)
    for pr in prs:
        ado_pull_requests_api.abandon_pull_request(repository_id, pr.id)
    print("All PRs have been abandoned.")


@task
def build_worker_image(ctx):
    ctx.run("docker build -f devops/docker/job.Dockerfile -t task-automation:latest .")


@task
def find_working_pytest_celery_version(c):
    """
    Test different versions of pytest-celery to find a working one.
    """

    def run_test(version):
        print(f"Testing pytest-celery version {version}")

        # Uninstall current version
        c.run(f"{sys.executable} -m pip uninstall -y pytest-celery", warn=True)

        # Install specific version
        result = c.run(f"{sys.executable} -m pip install pytest-celery=={version}", warn=True)

        if result.failed:
            print(f"Failed to install pytest-celery {version}")
            print(result.stderr)
            return False

        # Run pytest
        result = c.run("pytest tests/test_crew/test_load_tools.py", warn=True)

        if result.ok:
            print(f"pytest-celery {version} works!")
            return True
        else:
            print(f"pytest-celery {version} failed")
            print(result.stderr)
            return False

    # List of versions to test, from newest to oldest
    versions = [
        "1.0.0", "0.1.0", "0.0.9", "0.0.8", "0.0.7", "0.0.6", "0.0.5", "0.0.4", "0.0.3", "0.0.2", "0.0.1"
    ]

    for version in versions:
        if run_test(version):
            print(f"Found working version: {version}")
            break
    else:
        print("No working version found")


@task
def test(c):
    """
    Run the test suite.
    """
    c.run("pytest -m 'not requires_llm'")