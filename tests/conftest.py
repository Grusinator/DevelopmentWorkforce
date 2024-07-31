import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from random import randint

import pytest

from src.devops_integrations.repos.ado_repos_models import RepositoryModel, ProjectModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel


@pytest.fixture(scope="function")
def create_test_workspace_repo():
    guid = str(uuid.uuid4())[0:8]
    time = datetime.now().strftime("%m-%d-%H-%M-%S")
    working_directory = Path.cwd() / "test_workspace" / f"{time}_{guid}"
    os.makedirs(working_directory)
    yield working_directory


_id_gen = (i for i in range(100))


class SimpleWorkItemModel(WorkItemModel):

    def __init__(self, **kwargs):
        _id = next(_id_gen)
        params = dict(source_id=_id, type="User Story", state="New", title=f"task {_id}")
        params.update(kwargs)
        super().__init__(**params)


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
def dummy_work_items():
    return [
        SimpleWorkItemModel(description="create "),
        SimpleWorkItemModel(description="Description for task 2")
    ]


def run_pytest_in_workspace(workspace_dir: Path):
    pytest_result = subprocess.run(
        ['pytest', str(workspace_dir), '--json-report', '--json-report-file=pytest_report.json'],
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )
    json_report_path = workspace_dir / 'pytest_report.json'
    assert json_report_path.exists(), f"Report file not found: {json_report_path}"
    with open(json_report_path, 'r') as report_file:
        report_data = json.load(report_file)
        assert report_data['summary']['total'] > 0
        assert pytest_result.returncode == 0, report_data


@pytest.fixture
def mock_work_item():
    work_item = WorkItemModel(
        source_id=randint(1, 99999),
        title="Test Task",
        description="This is a test task",
        assigned_to="William Sandvej Hansen",
        state="New",
        type="User Story"
    )
    return work_item


@pytest.fixture
def mock_repository() -> RepositoryModel:
    repo_url = os.getenv("ADO_REPO_URL")
    repo_name = os.getenv("ADO_REPO_NAME")

    project_model = ProjectModel(id=2, name="test", source_id="test")
    return RepositoryModel(id=2, source_id="test", name=repo_name, git_url=repo_url, project=project_model)
