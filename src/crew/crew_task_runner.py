from pathlib import Path

from crewai import Task, Crew

from src.ado_integrations.workitems.ado_workitem_models import WorkItem
from src.crew.crew_ai_agents import CrewAiAgents
from src.crew.crew_ai_models import CrewAiModels


class CrewTaskRunner:

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.agency = CrewAiAgents(workspace_dir)
        self.default_agent = None
        self.agents = []
        self.tasks = []
        self.crew = None

    def add_developer_agent(self):
        self.default_agent = self.agency.create_developer()
        self.agents.append(self.default_agent)

    def add_task_from_work_item(self, work_item: WorkItem):
        task = Task(
            description=f"""complete below work item by writing code to files based on the requirements and the acceptance 
                    criteria from user stories. Use the tools to write files, 
                    the infrastructure will handle the rest, eg. cloning repo, pushing etc.
                    
                    write unit tests that match the acceptance criteria, 
                    and run the tests to verify that its implemented correctly.

                    the user story looks like this:
                    {work_item.title}

                    {work_item.description}

                    """,
            agent=self.default_agent,
            expected_output='if succeeded return "SUCCEEDED" otherwise return "FAILED"'
        )
        self.tasks.append(task)

    def add_test_task(self, work_item: WorkItem):
        test = Task(
            description=f"""test the app, by addding unit tests to the repository
                     based on the requirements and the acceptance criteria from user stories,

                     add a test and write in the name of the function the user story id for backtracking..

                     {work_item.id}
                     {work_item.description}
                     """,
            expected_output='if succeeded return "SUCCEEDED" otherwise return "FAILED"',
            agent=self.default_agent
        )
        self.tasks.append(test)

    def run(self):
        self.crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=2,  # You can set it to 1 or 2 to different logging levels
            # manager_llm=default_llm,
            # process=Process.hierarchical,
            # allow_delegation=True
            # function_calling_llm=CrewAiModels.ollama_instruct

        )
        return self.crew.kickoff()
