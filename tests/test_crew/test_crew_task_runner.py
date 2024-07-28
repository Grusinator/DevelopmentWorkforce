
import pytest

from src.crew.crew_task_runner import CrewTaskRunner
from tests.conftest import SimpleWorkItem, run_pytest_in_workspace


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





