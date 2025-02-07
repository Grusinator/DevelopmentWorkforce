import textwrap
from pathlib import Path

from crewai import Task, Crew, Process
from loguru import logger

from src.crew.models import TaskResult, LocalDevelopmentResult
from src.devops_integrations.pull_requests.pull_request_models import PullRequestCommentModel, \
    PullRequestCommentThreadModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
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
        self.result: LocalDevelopmentResult = LocalDevelopmentResult(succeeded=False)

    def add_developer_agent(self):
        self.default_agent = self.agency.create_developer()
        self.agents.append(self.default_agent)

    def add_task_from_work_item(self, work_item: WorkItemModel, extra_info=None):
        description = f"""
        complete below work item by writing code to files based on the requirements
        and the acceptance criteria from user stories.
        Use the tools to write files, the infrastructure will handle the rest, eg. cloning repo, pushing etc.

        write unit tests that match the acceptance criteria,
        and run the tests to verify that its implemented correctly.

        the user story looks like this:
        {work_item.title}

        {work_item.description}

        """
        task = Task(
            description=textwrap.dedent(description).lstrip(),
            agent=self.default_agent,
            expected_output='if succeeded return "SUCCEEDED" otherwise return "FAILED"'
        )
        self.tasks.append(task)
        task_result = TaskResult(task_id=str(task.id), work_item_id=work_item.source_id)
        self.result.task_results.append(task_result)

    def add_task_handle_comment_thread(self, comment_thread: PullRequestCommentThreadModel, work_item: WorkItemModel):
        comment_thread_formatted = comment_thread.pretty_format()
        description = f"""
                Your main objective is to return a reply to the given comment thread:
                
                {comment_thread_formatted}

                the comment is related to this user story, just for context. 
                do not try to solve the US unless related to the latest comment:
                
                {work_item.title}

                {work_item.description}
                reply as if you were to respond to the comment after trying to solve it. 
                Feel free write files if needed.
                """
        task = Task(
            description=textwrap.dedent(description).lstrip(),
            agent=self.default_agent,
            expected_output='a response to the comment thread'
        )
        self.tasks.append(task)
        task_result = TaskResult(task_id=str(task.id), thread_id=comment_thread.id, work_item_id=work_item.source_id)
        self.result.task_results.append(task_result)

    def add_test_task(self, work_item: WorkItemModel):
        test = Task(
            description=f"""test the app, by addding unit tests to the repository
                     based on the requirements and the acceptance criteria from user stories,

                     add a test and write in the name of the function the user story id for backtracking..

                     {work_item.source_id}
                     {work_item.description}
                     """,
            expected_output='if succeeded return "SUCCEEDED" otherwise return "FAILED"',
            agent=self.default_agent
        )
        self.tasks.append(test)

    def run(self) -> LocalDevelopmentResult:
        self.crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=2,  # You can set it to 1 or 2 to different logging levels
            manager_llm=CrewAiModels.default_llm,
            process=Process.hierarchical,
            # allow_delegation=True
            # function_calling_llm=CrewAiModels.ollama_instruct

        )
        result = self.crew.kickoff()
        self.result.succeeded = "SUCCEEDED" == self.clean_crew_ai_result_string(result)
        return self.update_task_results()

    def update_task_results(self) -> LocalDevelopmentResult:
        for crew_task in self.crew.tasks:
            try:
                matching_task = [task_result for task_result in self.result.task_results if task_result.task_id == str(crew_task.id)][0]
            except IndexError:
                raise IndexError(f"Task {crew_task.id} not found in task results")
            else:
                matching_task.output = self.clean_crew_ai_result_string(crew_task.output.result)

        return self.result

    def clean_crew_ai_result_string(self, result: str) -> str:
        return result.replace("`", "").lstrip().rstrip()