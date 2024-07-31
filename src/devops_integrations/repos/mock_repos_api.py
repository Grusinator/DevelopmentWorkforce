from typing import List
from src.devops_integrations.repos.ado_repos_models import ProjectModel, RepositoryModel
from src.devops_integrations.repos.base_repos_api import BaseReposApi


class MockReposApi(BaseReposApi):
    def get_repository_id(self, repo_name: str) -> str:
        return "mock-repo-id"

    def get_repository(self, repo_name: str) -> RepositoryModel:
        return RepositoryModel(
            id="mock-repo-id",
            name=repo_name,
            url="http://mock.url/repo"
        )

    def get_projects(self) -> List[ProjectModel]:
        return [
            ProjectModel(id="mock-project-id", name="Mock Project")
        ]

    def get_repositories(self, project_id: str) -> List[RepositoryModel]:
        return [
            RepositoryModel(id="mock-repo-id", name="Mock Repo", url="http://mock.url/repo")
        ]

    def branch_exists(self, repository_id: str, branch_name: str) -> bool:
        return branch_name == "existing-branch"

    def create_branch(self, repository_id: str, branch_name: str, source_branch: str) -> None:
        pass  # Mocked method does nothing
