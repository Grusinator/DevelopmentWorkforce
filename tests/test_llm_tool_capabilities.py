from datetime import datetime
from pathlib import Path
import pytest
from crewai import Task, Crew
from dotenv import load_dotenv
from development_workforce.ado_integrations.mock_ado_workitems_api import MockAdoWorkitemsApi
from development_workforce.crew.tools import ToolsBuilder
from development_workforce.crew.crew import tester
from development_workforce.crew.models import get_llm
import os
from uuid import uuid4


@pytest.fixture(autouse=True)
def load_env_vars():
    load_dotenv(".env", override=True)


@pytest.fixture
def create_toolset(create_working_dir):
    git_url = "https://github.com/Grusinator/ai-test-project.git"
    ado_workitems_api = MockAdoWorkitemsApi()  # Assuming this is initialized elsewhere as per original script

    tools_list = ToolsBuilder(create_working_dir) \
        .add_search_tools() \
        .add_ado_tools(ado_workitems_api) \
        .add_file_management_tools() \
        .add_pytest_tool() \
        .add_git_tools(git_url, main_branch_name="automated_testing") \
        .build()

    return tools_list


@pytest.fixture
def instantiate_llm(request):
    llm_name = request.param
    return get_llm(llm_name)


@pytest.fixture
def agent_tester(create_toolset, instantiate_llm):
    tester.tools = create_toolset
    tester.llm = instantiate_llm
    return tester


@pytest.fixture
def tool_test_task(request, agent_tester):
    tool_name = request.param
    description = f"""Test the tool: '{tool_name}' to see if it behaves as expected. 
    Setup a test case, and respond with 'TOOL WORKS' if you managed to run the tool successfully. "
    If it does not work the first time, try another way for a couple of iterations to make sure
    that it's not just the inputs that are wrong."""
    return Task(
        description=description,
        expected_output="'TOOL WORKS' if the tool works, 'TOOL BROKEN' if not",
        agent=agent_tester
    )


@pytest.mark.parametrize("instantiate_llm", ["chatgpt", ], indirect=True)
@pytest.mark.parametrize("tool_test_task", [
    # "get work item (1)",
    # "List ado",
    # "Create work item",
    # "Update work item",
    # "delete work item",
    # "create file",
    # "delete file",
    # "get file",
    # "get file list",
    # "run pytests",
    # "git commit a test file",
    # "create git branch",
    "push test file to origin git"
], indirect=True)
def test_run_tool(instantiate_llm, tool_test_task, agent_tester):
    crew = Crew(
        agents=[agent_tester],
        tasks=[tool_test_task],
        verbose=2,
        llm=instantiate_llm,
    )
    result = crew.kickoff()
    assert result == "TOOL WORKS"


@pytest.mark.parametrize("instantiate_llm", ["chatgpt", ], indirect=True)
@pytest.mark.parametrize("instruction", [
    # "write a small python test that asserts that 1 + 1 equals 2, and run the python test locally",
    "write a function in one file, and a test in another. and run the test",
    "pull from the origin repo, create a new branch, add a file and push the branch to origin"
])
def test_run_instruction(instruction, agent_tester, instantiate_llm):
    task = Task(
        description=instruction,
        expected_output="'OBJECTIVE COMPLETED' if the you managed to complete, 'OBJECTIVE FAILED' if not",
        agent=agent_tester
    )
    crew = Crew(
        agents=[agent_tester],
        tasks=[task],
        verbose=2,
        llm=instantiate_llm,
    )
    result = crew.kickoff()
    assert result == "OBJECTIVE COMPLETED"

