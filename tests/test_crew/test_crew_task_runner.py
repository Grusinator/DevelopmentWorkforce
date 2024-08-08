
import pytest

from src.crew.crew_task_runner import CrewTaskRunner
from tests.run_pytest_in_workspace import run_pytest_in_workspace


@pytest.mark.requires_llm
@pytest.mark.parametrize("work_item_description", [
    "As a user, I want a Python function that calculates the factorial of a given number so that I can use it for mathematical computations.",
    # "As a user, I want a Python function that sorts a list of numbers in ascending order so that I can organize data efficiently.",
    # "As a user, I want a Python function that finds the maximum value in a list of numbers so that I can determine the largest number in the dataset.",
    # "As a user, I want a Python function that checks if a given string is a palindrome so that I can identify symmetrical words or phrases.",
    # "As a user, I want a Python function that generates the Fibonacci sequence up to a given number of terms so that I can use it for mathematical modeling."
])
def test_parameterized_developer_task_runner(workspace_dir, work_item_description, work_item_model):
    runner = CrewTaskRunner(workspace_dir)
    runner.add_developer_agent()
    work_item_model.description = work_item_description
    runner.add_task_from_work_item(work_item_model)

    result = runner.run()

    assert "SUCCEEDED" in result

    run_pytest_in_workspace(workspace_dir)





