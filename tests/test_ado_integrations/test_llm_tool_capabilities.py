import pytest
from crewai import Task, Crew
from dotenv import load_dotenv
from development_workforce.crew.crew import tester
from development_workforce.crew.models import get_llm


@pytest.fixture(autouse=True)
def load_env_vars():
    load_dotenv(".env", override=True)


@pytest.fixture
def instantiate_llm(request):
    llm_name = request.param
    return get_llm(llm_name)

@pytest.fixture
def tool_test_task(request):
    tool_name = request.param
    description = f"""Test the tool: '{tool_name}' to see if it behaves as expected. 
    Setup a test case, and respond with 'TOOL WORKS' if you managed to run the tool successfully. "
    If it does not work the first time, try another way for a couple of iterations to make sure
    that it's not just the inputs that are wrong."""
    return Task(
        description=description,
        expected_output="'TOOL WORKS' if the tool works, 'TOOL BROKEN' if not",
        agent=tester
    )


@pytest.mark.parametrize("instantiate_llm", ["chatgpt", ], indirect=True)
@pytest.mark.parametrize("tool_test_task", [
    # "get work item (1)",
    # "List ado",
    # "Create work item",
    # "Update work item",
    # "delete work item",
    "create file",
    "delete file",
    "get file",
    "get file list",
    "run pytests",
    "git commit a test file"
], indirect=True)
def test_run_tool(instantiate_llm, tool_test_task):
    crew = Crew(
        agents=[tester],
        tasks=[tool_test_task],
        verbose=2,
        llm=instantiate_llm,
    )
    result = crew.kickoff()
    assert result == "TOOL WORKS"
