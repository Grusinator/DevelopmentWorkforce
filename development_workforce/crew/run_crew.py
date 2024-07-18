from crewai import Task, Crew

from development_workforce.ado_integrations.workitems.ado_workitem_models import AdoWorkItem
from development_workforce.crew.agents import Agents


class CrewTaskRunner:

    def run(self, work_item: AdoWorkItem, workspace_dir):
        self.get_agents(workspace_dir)
        self.create_tasks(work_item)
        self.create_crew()
        return self.crew.kickoff()

    def get_agents(self, workspace_dir):
        self.agents = Agents(workspace_dir).create_agents()
        self.developer = self.agents["developer"]
        self.tester = self.agents["tester"]
        self.product_owner = self.agents["product_owner"]
        self.scrum_master = self.agents["scrum_master"]

    def create_tasks(self, work_item):
        research_user_stories = Task(
            description="""research the user stories, by using the ado search tool
             to find information about the user stories and the acceptance criteria""",
            expected_output="a list of current items in ado, if the tools fail, return me the error message from the tool",
            agent=self.product_owner
        )

        define_project_scope = Task(
            description="""develop the software project by breaking down the project described in ADO into subtasks. 
          prepare each task with a description and acceptance criteria. 
          Make sure all team members approve the list of tasks, 
          upload task descriptions to ADO using the create and update tools.""",
            expected_output="an extensive list of tasks required to complete the project, "
                            "with descriptions and acceptance criteria, uploaded to ADO",
            agent=self.product_owner
        )

        test = Task(
            description=f"""test the app, by addding unit tests to the repository
             based on the requirements and the acceptance criteria from user stories,
             
             add a test and write in the name of the function the user story id for backtracking..
             
             {work_item.id}
             """,


            agent=self.tester
        )

        development = Task(
            description=f"""develop the app, by writing code to files based on the requirements and the acceptance 
            criteria from user stories. Use the tools to write files, 
            the infrastructure will handle the rest, eg. cloning repo, pushing etc.
            
            the user story looks like this:
            {work_item.title}
            
            {work_item.description}
            
            """,
            agent=self.developer
        )

        self.tasks = [development, test]

    def create_crew(self):
        # Instantiate your crew with a sequential process
        self.crew = Crew(
            agents=[self.developer],
            tasks=self.tasks,
            verbose=2,  # You can set it to 1 or 2 to different logging levels
            # manager_llm=default_llm,
            # process=Process.hierarchical,
            # allow_delegation=True
        )


if __name__ == "__main__":
    runner = CrewTaskRunner()
    runner.run("This is a test task", "../../test_workspace/test123")
