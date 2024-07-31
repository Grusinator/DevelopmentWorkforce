from abc import ABC, abstractmethod
from typing import List
from src.devops_integrations.repos.ado_repos_models import Project, Repository


class BaseReposApi(ABC):
    @abstractmethod
    def get_repository_id(self, repo_name: str) -> str:
        pass

    @abstractmethod
    def get_repository(self, repo_name: str) -> Repository:
        pass

    @abstractmethod
    def get_projects(self) -> List[Project]:
        pass

    @abstractmethod
    def get_repositories(self, project_id: str) -> List[Repository]:
        pass

    @abstractmethod
    def branch_exists(self, repository_id: str, branch_name: str) -> bool:
        pass

    @abstractmethod
    def create_branch(self, repository_id: str, branch_name: str, source_branch: str) -> None:
        pass
