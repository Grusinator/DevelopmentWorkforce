import os
from pathlib import Path
from typing import List

from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_core.tools import BaseTool

from development_workforce.ado_integrations.ado_workitems_api_tools import instantiate_ado_tools
from development_workforce.ado_integrations.mock_ado_workitems_api import MockAdoWorkitemsApi
from development_workforce.ado_integrations.ado_models import AdoWorkItem, CreateWorkItemInput
from langchain_community.agent_toolkits import FileManagementToolkit
from tempfile import TemporaryDirectory
from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_openai import ChatOpenAI
import pytest

from development_workforce.git_tool.git_tool import instantiate_git_tools

# Set your environment variables using os.environ
os.environ["GITHUB_APP_ID"] = "123456"
os.environ["GITHUB_APP_PRIVATE_KEY"] = "path/to/your/private-key.pem"
os.environ["GITHUB_REPOSITORY"] = "username/repo-name"
os.environ["GITHUB_BRANCH"] = "bot-branch-name"
os.environ["GITHUB_BASE_BRANCH"] = "main"

# This example also requires an OpenAI API key
os.environ["OPENAI_API_KEY"] = ""

llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")
github = GitHubAPIWrapper()
toolkit = GitHubToolkit.from_github_api_wrapper(github)
github_tools = toolkit.get_tools()

search_tools = [DuckDuckGoSearchRun()]

ado_workitems_api = MockAdoWorkitemsApi()
workitem = CreateWorkItemInput(
    type="Epic",
    assigned_to="John",
    title="Make a tick tac toe game",
    description="update the description",
    tags=[]
)
ado_workitems_api.create_work_item(workitem)
ado_workitems_tools = instantiate_ado_tools(ado_workitems_api=ado_workitems_api)

working_directory = Path("workspace/")
working_directory = TemporaryDirectory()
toolkit = FileManagementToolkit(
    root_dir=str(working_directory.name)
)  # If you don't provide a root_dir, operations will default to the current working directory
file_mgt_tools = toolkit.get_tools()




class PytestTool(BaseTool):
    """This tool runs pytest in the working directory"""
    def run(self):
        pytest.main([str(working_directory)])

pytest_tool = [PytestTool()]

git_tools = instantiate_git_tools()

default_tools: List[BaseTool] = (
    search_tools +
    ado_workitems_tools +
    file_mgt_tools +
    github_tools +
    pytest_tool +
    git_tools
)