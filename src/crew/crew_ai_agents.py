from pathlib import Path

from crewai import Agent

from src.crew.crew_ai_models import CrewAiModels
from src.crew.tools import ToolsBuilder


class CrewAiAgents:

    def __init__(self, workspace_dir):
        self.working_directory = Path(workspace_dir)
        self.tools_builder = ToolsBuilder(self.working_directory)
        self.tools = self.tools_builder.get_default_toolset()
        self.models = CrewAiModels()

    def create_generic(self):
        return Agent(
            role='Developer',
            goal='implement the feature or bug given by the task',
            backstory="""""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.models.developer_llm
        )

    def create_developer(self):
        return Agent(
            role='Developer',
            goal='implement the feature or bug given by the task, '
                 'if succeeded return "SUCCEEDED" otherwise return "FAILED"',
            backstory="""You are a talented Developer, responsible for writing code and implementing the
            features of the software application of highest quality.
            You are trying to be as accurate with each iteration, by writing specific, testable code
            you always update the files with a complete file, with all the previous functions. No "other funcs remain unchanged" 
            You prefer writing small files, where possible, to avoid fewer updates of large files. 
            """

            """
            Your development workflow looks like this:
            * read and understand the user story given as input
            * read and understand the existing codebase by leveraging the list workspace and search for files tools.
            * search online for information that you might need to implement the story
            * write complete full code files and classes to the workspace, no pseudocode or incomplete files.
             consider reading the file you are planning to write to on beforehand.
            * write test files to the workspace
            * run the pytest tool command to verify the code
            ** iterate steps until the tests have passed and all acceptance criteria have been fulfilled
            * if not possible after multiple attempts, return FAILED, otherwise return SUCCEEDED"""

            ,
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.models.developer_llm
        )

    def create_tester(self):
        return Agent(
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

    def create_scrum_master(self):
        return Agent(
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

    def create_product_owner(self):
        return Agent(
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
