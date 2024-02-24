import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_community.llms.ollama import Ollama
from development_workforce.ado_integrations.ado_workitems_api_tools import instantiate_ado_tools
from development_workforce.ado_integrations.mock_ado_workitems_api import MockAdoWorkitemsApi
from development_workforce.ado_integrations.ado_models import AdoWorkItem, CreateWorkItemInput

load_dotenv(".env", override=True)


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
        "max_new_tokens": 2000,  # Adjust based on input size to keep total under 1024
        # "top_k": 50,
        # "temperature": 0.2,
        "repetition_penalty": 1.1,
        "max_length": 4000,  # Ensure input + max_new_tokens <= 1024
    }
)


def get_llm(llm_name):
    llm_mapping = {
        "ollama_instruct": ollama_instruct,
        "ollama_python": ollama_python,
        "chatgpt": chatgpt,
        "hugging_face": hugging_face
    }
    llm = llm_mapping.get(llm_name)
    if llm is None:
        raise ValueError(f"Invalid llm_name: {llm_name}")


default_llm = chatgpt
developer_llm = default_llm

# from langchain_community.tools.file_management import CopyFileTool, DeleteFileTool, FileSearchTool, ListDirectoryTool, MoveFileTool, ReadFileTool, WriteFileTool

search_tool = DuckDuckGoSearchRun()

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

tools = [search_tool] + ado_workitems_tools

product_owner = Agent(
    role='Product Owner',
    goal='Define and prioritize product features',
    backstory="""You are an experienced Product Owner, responsible for defining the vision and roadmap of the product. 
    You work closely with stakeholders and development teams to ensure the product meets customer needs. 
    Make sure that all tasks are described in full detail and approved by the developers, before setting the state to ready for development.
    your primary interface is the board, using the ado tools.""",
    verbose=True,
    allow_delegation=True,
    tools=tools,
    llm=default_llm
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
    tools=tools,
    llm=default_llm
)

tester = Agent(
    role='QA Tester',
    goal='Ensure the quality of the product',
    backstory="""You are a skilled QA Tester, responsible for ensuring the quality of the product. 
  You perform various tests to identify any issues or bugs in the software.
  You are responisble for reviewing all the unit tests and make sure that the code is tested according to the acceptance criteria.""",
    verbose=True,
    allow_delegation=True,
    tools=tools,
    llm=default_llm
)

developer = Agent(
    role='Developer',
    goal='Develop the software application',
    backstory="""You are a talented Developer, responsible for writing code and implementing the features of the software application. 
  You have expertise in various programming languages and technologies. You are responsible for raising consern if the acceptance criteria
  are not clear and testable. You shold come up with a short description to each task on how to implement it.""",
    verbose=True,
    allow_delegation=False,
    tools=tools,
    llm=developer_llm
)
