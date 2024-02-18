import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
import os
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_community.llms.ollama import Ollama

from ado_integrations.ado_workitems_api_tools import AdoWorkitemsApiTools
from ado_integrations.mock_ado_workitems_api import MockAdoWorkitemsApi

load_dotenv()

ollama_instruct = Ollama(
    model=os.getenv("OLLAMA_MODEL_NAME"),
    base_url=os.getenv("OLLAMA_API_BASE")
)

ollama_python = Ollama(
    model=os.getenv("OLLAMA_MODEL_NAME_2"),
    base_url=os.getenv("OLLAMA_API_BASE_2")
)

chatgpt = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("OPENAI_MODEL_NAME"),
)

hugging_face = HuggingFaceEndpoint(
    endpoint_url=os.getenv("HUGGINGFACE_API_BASE"), 
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY"),
    task="text-generation",
    model_kwargs={
        "max_new_tokens": 1000,  # Adjust based on input size to keep total under 1024
        "top_k": 50,
        "temperature": 0.7,
        "repetition_penalty": 1.03,
        "max_length": 15000,  # Ensure input + max_new_tokens <= 1024
    }
)



default_llm = chatgpt
developer_llm = default_llm
print(default_llm)

# from langchain_community.tools.file_management import CopyFileTool, DeleteFileTool, FileSearchTool, ListDirectoryTool, MoveFileTool, ReadFileTool, WriteFileTool

search_tool = DuckDuckGoSearchRun()

api = MockAdoWorkitemsApi()
ado_api_tools = AdoWorkitemsApiTools(ado_workitems_api=api)


tools = [] + ado_api_tools.get_tools()

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
  llm=default_llm
)


developer = Agent(
  role='Developer',
  goal='Develop the software application',
  backstory="""You are a talented Developer, responsible for writing code and implementing the features of the software application. You have expertise in various programming languages and technologies.""",
  verbose=True,
  allow_delegation=False,
  tools=tools,
  llm=developer_llm
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
  manager_llm=default_llm,
  process=Process.hierarchical
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)