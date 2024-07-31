import pytest
from crewai import Task, Crew, Agent
from dotenv import load_dotenv

from src.devops_integrations.workitems.ado_workitem_models import CreateWorkItemInputModel
from src.devops_integrations.workitems.mock_workitems_api import MockWorkitemsApi
from src.crew.crew_ai_models import CrewAiModels
from src.crew.tools import ToolsBuilder


@pytest.fixture(autouse=True)
def load_env_vars():
    load_dotenv(".env", override=True)


@pytest.fixture
def create_toolset(workspace_dir_with_codebase):
    git_url = "https://github.com/Grusinator/ai-test-project.git"
    ado_workitems_api = MockWorkitemsApi()  # Assuming this is initialized elsewhere as per original script
    ado_workitems_api.create_work_item(
        CreateWorkItemInputModel(
            title="maka a calculator widget",
            description="This is a widget that can add, sub, div, and mul numbers",
            type="Feature",
            state="New"
        )
    )

    tools_list = (
        ToolsBuilder(workspace_dir_with_codebase)
        .add_search_tools()
        .add_ado_tools(ado_workitems_api)
        .add_file_management_tools()
        .add_pytest_tool()
        # .add_git_tools(git_url, main_branch_name="automated_testing")
        # .add_github_tools() \
        .add_invoke_tools()
        .build()
    )

    return tools_list


@pytest.fixture
def instantiate_llm(request):
    llm_name = request.param
    return CrewAiModels.get_llm(llm_name)


@pytest.fixture
def agent_tester(create_toolset, instantiate_llm):
    return Agent(
        role='QA Tester',
        goal='Ensure the quality of the product',
        backstory="""You are a skilled QA Tester, responsible for ensuring the quality of the product.
      You perform various tests to identify any issues or bugs in the software.
      You are responisble for reviewing all the unit tests and make sure that the code is tested
      according to the acceptance criteria.""",
        verbose=True,
        allow_delegation=True,
        tools=create_toolset,
        llm=instantiate_llm
    )


@pytest.fixture
def tool_test_task(request, agent_tester):
    tool_name = request.param
    description = f"""Test the tool: '{tool_name}' to see if it behaves as expected.
    Setup a test case, and respond with 'TOOL WORKS' if you managed to run the tool successfully.
    If it does not work the first time, try another way for a couple of iterations to make sure
    that it's not just the inputs that are wrong."""
    return Task(
        description=description,
        expected_output="'TOOL WORKS' if the tool works, 'TOOL BROKEN' if not",
        agent=agent_tester
    )



@pytest.mark.requires_llm
@pytest.mark.parametrize("instantiate_llm", ["chatgpt", ], indirect=True)
@pytest.mark.parametrize("tool_test_task", [
    "get work item (1)",
    "List ado",
    "Create work item",
    "Update work item",
    "delete work item",
    "create file",
    "delete file",
    "get file",
    "get file list",
    "run pytests",
    "git commit a test file",
    "create git branch",
    "create pull request",
    "push test file to origin git"
    "read_multiple_files"
    "format and lint using ruff"
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

@pytest.mark.skip("not usefull yet")
@pytest.mark.requires_llm
@pytest.mark.parametrize("instantiate_llm", ["chatgpt", ], indirect=True)
@pytest.mark.parametrize("instruction", [
    # "write a small python test that asserts that 1 + 1 equals 2, and run the python test locally",
    # "write a function in one file, and a test in another. and run the test",
    # "pull from the origin repo, create a new branch, add a file and push the branch to origin",
    # "write a user story and add it to ado",
    "list user stories, pick one and implement the story, by cloning, creating a branch, commit files and pushing the branch to origin",
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
