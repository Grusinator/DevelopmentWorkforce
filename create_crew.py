from dotenv import load_dotenv
import os
load_dotenv()

from crewai import Agent, Task, Crew, Process

os.environ["OPENAI_API_BASE"]='http://192.168.0.46:11434/v1'
os.environ["OPENAI_MODEL_NAME"]='openhermes'
os.environ["OPENAI_API_KEY"]=''


from ado_integrations.ado_tools import ado_tools

from langchain_community.llms import Ollama
codellama_llm = Ollama(model="codellama:7b")
default_llm = Ollama(model="openhermes:latest")
default_llm = codellama_llm # for now keep it simple  

from langchain_community.tools import DuckDuckGoSearchRun
# from langchain_community.tools.file_management import CopyFileTool, DeleteFileTool, FileSearchTool, ListDirectoryTool, MoveFileTool, ReadFileTool, WriteFileTool

search_tool = DuckDuckGoSearchRun()



tools = [] + ado_tools

product_owner = Agent( 
    role='Product Owner', 
    goal='Define and prioritize product features', 
    backstory="""You are an experienced Product Owner, responsible for defining the vision and roadmap of the product. You work closely with stakeholders and development teams to ensure the product meets customer needs. your primary interface is the board, using the ado tools.""", 
    verbose=True, 
    allow_delegation=True, 
    tools=tools,
    llm=default_llm 
)

scrum_master = Agent(
  role='Scrum Master',
  goal='Facilitate the development process',
  backstory="""You are a certified Scrum Master, responsible for ensuring the team follows the Scrum framework. You help the team to self-organize and remove any obstacles that may affect the development process.""",
  verbose=True,
  allow_delegation=True,
  tools=tools,
  llm=default_llm
)

tester = Agent(
  role='QA Tester',
  goal='Ensure the quality of the product',
  backstory="""You are a skilled QA Tester, responsible for ensuring the quality of the product. You perform various tests to identify any issues or bugs in the software.""",
  verbose=True,
  allow_delegation=True,
  tools=tools,
  llm=codellama_llm
)


developer = Agent(
  role='Developer',
  goal='Develop the software application',
  backstory="""You are a talented Developer, responsible for writing code and implementing the features of the software application. You have expertise in various programming languages and technologies.""",
  verbose=True,
  allow_delegation=False,
  tools=tools,
  llm=codellama_llm
)


research_user_stories = Task(
  description="""research the user stories, by using the ado search tool to find information about the user stories and the acceptance criteria""",
  expected_output="a list of acceptance criteria for the user stories in the ado backlog",
  agent=product_owner
)

define_project_scope = Task(
  description="""develop the software project by breaking down the project into subtasks in azure devops""",
  agent=product_owner
)

test = Task(
  description="""test the voting app, by addding unit tests to the repository based on the requirements and the acceptance criteria from user stories""",
  agent=tester
)

development = Task(
  description="""develop the voting app, by implementing the features of the software application, based on the requirements and the acceptance criteria from user stories. create pull requests and merge them to the main branch""",
  agent=developer
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[product_owner],
  tasks=[research_user_stories],
  verbose=2, # You can set it to 1 or 2 to different logging levels
  manager_llm=codellama_llm,
  process=Process.hierarchical
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)