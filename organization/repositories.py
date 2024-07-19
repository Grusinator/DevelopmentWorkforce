import os
from azure.devops.connection import Connection
from msrest.authentication import BasicTokenAuthentication


class AzureDevOpsRepository:
    def __init__(self, token):
        self.token = token
        self.connection = self._create_connection()

    def _create_connection(self):
        # Create a connection to the Azure DevOps organization using OAuth token
        credentials = BasicTokenAuthentication({"access_token": self.token})
        organization_url = os.getenv("AZURE_DEVOPS_ORGANIZATION_URL")
        connection = Connection(base_url=organization_url, creds=credentials)
        return connection

    def get_projects(self):
        # Get a client (the "core" client provides access to projects, teams, etc)
        core_client = self.connection.clients.get_core_client()
        # Get the first page of projects
        get_projects_response = core_client.get_projects()
        projects = []
        while get_projects_response is not None:
            for project in get_projects_response.value:
                projects.append(project)
            if get_projects_response.continuation_token is not None and get_projects_response.continuation_token != "":
                # Get the next page of projects
                get_projects_response = core_client.get_projects(
                    continuation_token=get_projects_response.continuation_token)
            else:
                # All projects have been retrieved
                get_projects_response = None
        return projects

    def get_repositories(self, project_id):
        # Get a client for the Git services
        git_client = self.connection.clients.get_git_client()
        # Get the list of repositories in the specified project
        repositories = git_client.get_repositories(project_id)
        return repositories


if __name__ == "__main__":
    # Example usage
    token = os.getenv("AZURE_DEVOPS_TOKEN")  # Make sure to set your OAuth token in the environment variables
    az_repo = AzureDevOpsRepository(token)

    print("Fetching Projects...")
    projects = az_repo.get_projects()
    for project in projects:
        print(f"Project: {project.name} ({project.id})")

    if projects:
        project_id = projects[0].id
        print(f"\nFetching Repositories for Project ID: {project_id}")
        repos = az_repo.get_repositories(project_id)
        for repo in repos:
            print(f"Repository: {repo.name} ({repo.id})")
