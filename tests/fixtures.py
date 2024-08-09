import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from random import randint

import pytest

from src.devops_integrations.models import ProjectAuthenticationModel
from src.devops_integrations.repos.ado_repos_models import RepositoryModel, ProjectModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
import pytest
from src.devops_integrations.pull_requests.pull_request_models import PullRequestCommentThreadModel, \
    PullRequestCommentModel, PullRequestModel, ReviewerModel


# @pytest.fixture(autouse=False)
# def pytest_configure():
#     from celery.fixups.django import DjangoWorkerFixup
#     DjangoWorkerFixup.install = lambda x: None


@pytest.fixture(scope="function")
def create_test_workspace_repo():
    guid = str(uuid.uuid4())[0:8]
    time = datetime.now().strftime("%m-%d-%H-%M-%S")
    working_directory = Path.cwd() / "test_workspace" / f"{time}_{guid}"
    os.makedirs(working_directory)
    yield working_directory


@pytest.fixture(scope="function")
def workspace_dir(tmp_path):
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    sys.path.insert(0, str(workspace_dir))
    yield workspace_dir
    sys.path.pop(0)
    try:
        shutil.rmtree(workspace_dir)
    except Exception:
        pass


@pytest.fixture(scope="function")
def workspace_dir_w_git(workspace_dir):
    subprocess.run(['git', 'init'], cwd=workspace_dir)
    yield workspace_dir


@pytest.fixture(scope="function")
def workspace_dir_with_codebase(workspace_dir):
    file_contents = {
        "file1.py": "def add(a, b):\n    return a + b\n",
        "file2.py": "def subtract(a, b):\n    return a - b\n",
        "file3.py": "def multiply(a, b):\n    return a * b\n",
        "nested/file4.py": "def divide(a, b):\n    return a / b\n",
        "nested/deep/file5.py": "def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n",
        ".git/file6.py": "def ignored_function():\n    return None\n",
        "test_add.py": "def test_add():\n    assert 1==1\n"
    }

    for filename, content in file_contents.items():
        file_path = workspace_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)

    yield workspace_dir  # Yield the temporary directory path for use in the test


@pytest.fixture(scope="function")
def workspace_dir_dummy_repo(workspace_dir):
    data_dir = Path.cwd() / "tests/dummy_repo"
    for file_path in data_dir.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(data_dir)
            destination_path = workspace_dir / relative_path
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(file_path, destination_path)

    yield workspace_dir  # Yield the temporary directory path for use in the test


@pytest.fixture
def work_item_model(agent_model):
    work_item = WorkItemModel(
        source_id=randint(1, 99999),
        title="Test Task",
        description="This is a test task",
        assigned_to=agent_model.agent_user_name,
        state="New",
        type="User Story"
    )
    return work_item


@pytest.fixture
def repository_model(agent_model) -> RepositoryModel:
    repo_url = os.getenv("ADO_REPO_URL")
    repo_name = os.getenv("ADO_REPO_NAME")

    project_model = ProjectModel(id=2, name="test", source_id="test")
    return RepositoryModel(id=2, source_id="test", name=repo_name, git_url=repo_url, project=project_model)


@pytest.fixture
def auth_model() -> ProjectAuthenticationModel:
    return ProjectAuthenticationModel(
        ado_org_name=os.getenv("ADO_ORGANIZATION_NAME"),
        pat=os.getenv("ADO_PERSONAL_ACCESS_TOKEN"),
        project_name=os.getenv("ADO_PROJECT_NAME")
    )

@pytest.fixture
def pull_request_model(repository_model, agent_model):
    return PullRequestModel(
            id=1,
            title="test",
            source_branch="feature",
            created_by_name=agent_model.agent_user_name,
            target_branch="main",
            status="active",
            repository=repository_model,
            reviewers=[ReviewerModel(
                source_id="test",
                display_name="",
                vote=-5
            )]
        )


@pytest.fixture
def comment_thread_model(pull_request_model, agent_model):
    return PullRequestCommentThreadModel(
        id=1,
        pull_request_source_id=pull_request_model.id,
        comments=[
            PullRequestCommentModel(
                id=1,
                created_by=agent_model.agent_user_name,
                created_date="2021-10-10",
                text="This is a test comment"
            )
        ]
    )
