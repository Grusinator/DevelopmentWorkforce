from typing import List
from src.devops_integrations.repos.ado_repos_models import ProjectModel, RepositoryModel
from src.devops_integrations.repos.base_repos_api import BaseReposApi


class MockReposApi(BaseReposApi):
    def __init__(self):
        self.repositories = []

    def get_repository_id(self, repo_name: str) -> str:
        for repo in self.repositories:
            if repo.name == repo_name:
                return repo.id
        raise ValueError(f"No repository found with name: {repo_name}")

    def get_repository(self, repo_name: str) -> RepositoryModel:
        for repo in self.repositories:
            if repo.name == repo_name:
                return repo
        raise ValueError(f"No repository found with name: {repo_name}")

    def get_projects(self) -> List[ProjectModel]:
        return [repo.project for repo in self.repositories]

    def get_repositories(self, project_id: str) -> List[RepositoryModel]:
        return [repo for repo in self.repositories if repo.project.id == project_id]

    def branch_exists(self, repository_id: str, branch_name: str) -> bool:
        return branch_name == "existing-branch"

    def create_branch(self, repository_id: str, branch_name: str, source_branch: str) -> None:
        pass  # Mocked method does nothing
