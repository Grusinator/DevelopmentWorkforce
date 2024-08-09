from abc import ABC, abstractmethod
from typing import List
from src.devops_integrations.repos.ado_repos_models import ProjectModel, RepositoryModel


class BaseReposApi(ABC):
    @abstractmethod
    def get_repository_id(self, repo_name: str) -> str:
        pass

    @abstractmethod
    def get_repository(self, repo_name: str) -> RepositoryModel:
        pass

    @abstractmethod
    def get_projects(self) -> List[ProjectModel]:
        pass

    @abstractmethod
    def get_repositories(self, project_id: str) -> List[RepositoryModel]:
        pass

    @abstractmethod
    def branch_exists(self, repository_id: str, branch_name: str) -> bool:
        pass

    @abstractmethod
    def create_branch(self, repository_id: str, branch_name: str, source_branch: str) -> None:
        pass

    def create_repository(self, repository_name: str, project_name: str) -> None:
        pass
