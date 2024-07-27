import json
import shutil
import subprocess
from pathlib import Path

import pytest

from src.ado_integrations.workitems.ado_workitem_models import WorkItem
from src.crew.crew_task_runner import CrewTaskRunner

_id_gen = (i for i in range(100))


class SimpleWorkItem(WorkItem):

    def __init__(self, **kwargs):
        _id = next(_id_gen)
        params = dict(id=_id, type="User Story", state="New", title=f"task {_id}")
        params.update(kwargs)
        super().__init__(**params)


@pytest.fixture
def workspace_dir(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    yield workspace
    shutil.rmtree(workspace)



@pytest.fixture
def dummy_work_items():
    return [
        SimpleWorkItem(description="create "),
        SimpleWorkItem(description="Description for task 2")
    ]

@pytest.mark.requires_llm
@pytest.mark.parametrize("work_item_description", [
    "As a user, I want a Python function that calculates the factorial of a given number so that I can use it for mathematical computations.",
    # "As a user, I want a Python function that sorts a list of numbers in ascending order so that I can organize data efficiently.",
    # "As a user, I want a Python function that finds the maximum value in a list of numbers so that I can determine the largest number in the dataset.",
    # "As a user, I want a Python function that checks if a given string is a palindrome so that I can identify symmetrical words or phrases.",
    # "As a user, I want a Python function that generates the Fibonacci sequence up to a given number of terms so that I can use it for mathematical modeling."
])
def test_parameterized_developer_task_runner(workspace_dir, work_item_description):
    runner = CrewTaskRunner(workspace_dir)
    runner.add_developer_agent()
    work_item = SimpleWorkItem(description=work_item_description)
    runner.add_task_from_work_item(work_item)

    result = runner.run()

    assert "SUCCEEDED" in result

    run_pytest_in_workspace(workspace_dir)

@pytest.mark.skip("not usefull yet")
@pytest.mark.requires_llm
def test_default_developer_task_runner(workspace_dir, dummy_work_items):
    runner = CrewTaskRunner(workspace_dir)
    runner.add_developer_agent()

    for work_item in dummy_work_items:
        runner.add_task_from_work_item(work_item)
        runner.add_test_task(work_item)

    result = runner.run()
    assert result is not None


def run_pytest_in_workspace(workspace_dir: Path):
    pytest_result = subprocess.run(
        ['pytest', str(workspace_dir), '--json-report', '--json-report-file=report.json'],
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )
    json_report_path = workspace_dir / 'report.json'
    assert json_report_path.exists(), f"Report file not found: {json_report_path}"
    with open(json_report_path, 'r') as report_file:
        report_data = json.load(report_file)
        assert report_data['summary']['total'] > 0

        assert pytest_result.returncode == 0, report_data
