import os

from pathlib import Path
from typing import List

from langchain.tools import BaseTool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_community.utilities.github import GitHubAPIWrapper

from src.ado_integrations.workitems.ado_workitems_api_tools import instantiate_ado_tools
from src.ado_integrations.workitems.mock_ado_workitems_api import MockAdoWorkitemsApi
from src.git_tool.git_abstraction import GitAbstraction
from src.git_tool.git_tool import instantiate_git_tools
from src.util_tools.pytest_tool import PytestTool


class ToolsBuilder:
    def __init__(self, working_directory: Path):
        self.tools: List[BaseTool] = []
        self.working_directory = working_directory
        self.private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")

    def get_default_toolset(self):
        return (
            self
            .add_search_tools()
            .add_file_management_tools()
            .add_pytest_tool()
            .build()
        )

    def add_search_tools(self):
        self.tools.append(DuckDuckGoSearchRun())
        return self

    def add_github_tools(self):
        github = GitHubAPIWrapper(github_app_private_key=self.private_key)
        toolkit = GitHubToolkit.from_github_api_wrapper(github)
        self.tools += toolkit.get_tools()
        return self

    def add_ado_tools(self, ado_workitems_api):
        ado_workitems_tools = instantiate_ado_tools(ado_workitems_api=ado_workitems_api)
        self.tools += ado_workitems_tools
        return self

    def add_file_management_tools(self):
        toolkit = FileManagementToolkit(root_dir=str(self.working_directory))
        file_mgt_tools = toolkit.get_tools()
        self.tools += file_mgt_tools
        return self

    def add_pytest_tool(self):
        self.tools.append(PytestTool(self.working_directory))
        return self

    def add_git_tools(self, git_url, main_branch_name="main"):
        git_abstraction = GitAbstraction(git_url, self.working_directory, main_branch_name)
        git_abstraction.clone_repo()
        git_tools = instantiate_git_tools(git_abstraction)
        self.tools += git_tools
        return self

    def build(self):
        return self.tools


# Usage example
if __name__ == "__main__":
    work_dir = Path("workspace/")
    _git_url = "https://github.com/Grusinator/ai-test-project.git"
    _ado_workitems_api = MockAdoWorkitemsApi()  # Assuming this is initialized elsewhere as per original script

    tools_list = ToolsBuilder(work_dir) \
        .add_search_tools() \
        .add_ado_tools(_ado_workitems_api) \
        .add_file_management_tools() \
        .add_pytest_tool() \
        .add_git_tools(_git_url) \
        .add_github_tools() \
        .build()

# tools_list now contains all the tools added through the builder pattern
