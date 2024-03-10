from crewai import Task, Crew

from development_workforce.crew.crew import product_owner, scrum_master, tester, developer
from development_workforce.crew.tools import ado_workitems_api

research_user_stories = Task(
    description="""research the user stories, by using the ado search tool
     to find information about the user stories and the acceptance criteria""",
    expected_output="a list of current items in ado, if the tools fail, return me the error message from the tool",
    agent=product_owner
)

define_project_scope = Task(
    description="""develop the software project by breaking down the project described in ADO into subtasks. 
  prepare each task with a description and acceptance criteria. 
  Make sure all team members approve the list of tasks, 
  upload task descriptions to ADO using the create and update tools.""",
    expected_output="an extensive list of tasks required to complete the project, "
                    "with descriptions and acceptance criteria, uploaded to ADO",
    agent=product_owner
)

test = Task(
    description="""test the app, by addding unit tests to the repository
     based on the requirements and the acceptance criteria from user stories""",
    agent=tester
)

development = Task(
    description="""develop the app, by implementing the features of the software application, 
    based on the requirements and the acceptance criteria from user stories. 
    create pull requests and merge them to the main branch""",
    agent=developer
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[product_owner, scrum_master, tester, developer],
    tasks=[research_user_stories, define_project_scope],
    verbose=2,  # You can set it to 1 or 2 to different logging levels
    # manager_llm=default_llm,
    # process=Process.hierarchical,
    # allow_delegation=True
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)

print(ado_workitems_api.work_items)
