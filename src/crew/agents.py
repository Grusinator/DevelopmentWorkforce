from pathlib import Path

from crewai import Agent
from dotenv import load_dotenv

from src.crew.models import Models
from src.crew.tools import ToolsBuilder

load_dotenv(".env", override=True)


git_url = "https://github.com/Grusinator/ai-test-project.git"


class Agents:

    def __init__(self, workspace_dir):
        self.working_directory = Path(workspace_dir)
        self.tools_builder = ToolsBuilder(self.working_directory)
        self.tools = self.setup_tools()
        self.models = Models()

    def setup_tools(self):
        tools_list = self.tools_builder \
            .add_search_tools() \
            .add_file_management_tools() \
            .add_pytest_tool() \
            .build()

        # .add_git_tools(git_url) \
        # .add_ado_tools(ado_workitems_api) \
        return tools_list

    def create_agents(self):
        product_owner = Agent(
            role='Product Owner',
            goal='Define and prioritize product features',
            backstory="""You are an experienced Product Owner, responsible for defining the vision and roadmap of the product. 
            You work closely with stakeholders and development teams to ensure the product meets customer needs. 
            Make sure that all tasks are described in full detail and approved by the developers, 
            before setting the state to ready for development.
            your primary interface is the board, using the ado tools.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=self.models.default_llm
        )

        scrum_master = Agent(
            role='Scrum Master',
            goal='Facilitate the development process',
            backstory="""You are a certified Scrum Master, responsible for ensuring the team follows the Scrum framework. 
          You help the team to self-organize and remove any obstacles that may affect the development process. 
          Make sure that all tasks are broken down into manageable tasks and assigned to the right team members.
          Make sure that all tasks have acceptance criteria""",

            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=self.models.default_llm
        )

        tester = Agent(
            role='QA Tester',
            goal='Ensure the quality of the product',
            backstory="""You are a skilled QA Tester, responsible for ensuring the quality of the product. 
          You perform various tests to identify any issues or bugs in the software.
          You are responisble for reviewing all the unit tests and make sure that the code is tested 
          according to the acceptance criteria.""",
            verbose=True,
            allow_delegation=True,
            tools=self.tools,
            llm=self.models.default_llm
        )

        developer = Agent(
            role='Developer',
            goal='Develop the software application',
            backstory="""You are a talented Developer, responsible for writing code and implementing the features of the software application. 
          You have expertise in various programming languages and technologies. You are responsible for raising consern if the acceptance criteria
          are not clear and testable. You shold come up with a short description to each task on how to implement it.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.models.developer_llm
        )
        return {
            'product_owner': product_owner,
            'scrum_master': scrum_master,
            'tester': tester,
            'developer': developer
        }
