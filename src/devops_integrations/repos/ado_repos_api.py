from typing import List

from azure.devops.v7_1.git import GitRefUpdate

from src.devops_integrations.ado_connection import ADOConnection
from src.devops_integrations.repos.ado_repos_models import Project, Repository
from src.devops_integrations.models import ProjectAuthentication
from src.devops_integrations.repos.base_repos_api import BaseReposApi


class ADOReposApi(ADOConnection, BaseReposApi):
    def __init__(self, auth: ProjectAuthentication):
        super().__init__(auth)

    def get_repository_id(self, repo_name: str) -> str:
        repositories = self.client.get_repositories(self.auth.project_name)
        repo = [repo for repo in repositories if repo.name == repo_name][0]
        return repo.id if repositories else None

    def get_repository(self, repo_name) -> Repository:
        repositories = self.client.get_repositories(self.auth.project_name)
        repo = [repo for repo in repositories if repo.name == repo_name][0]
        return self._to_repository(repo)

    def get_projects(self) -> List[Project]:
        projects = self.core_client.get_projects()
        project_list = []
        for project in projects:
            project_list.append(Project(
                name=project.name,
                id=project.id,
                source_id=project.id,
                description=project.description,
                url=project.url
            ))
        return project_list

    def get_repositories(self, project_id: str) -> List[Repository]:
        repositories = self.client.get_repositories(project_id)
        repo_list = []
        for repo in repositories:
            repo_list.append(self._to_repository(repo))
        return repo_list

    def branch_exists(self, repository_id: str, branch_name: str) -> bool:
        refs = self.client.get_refs(repository_id, filter=f"heads/{branch_name}")
        return len(refs) > 0

    def create_branch(self, repository_id: str, branch_name: str, source_branch: str) -> None:
        refs = self.client.get_refs(repository_id, filter=f"heads/{source_branch}")
        if not refs:
            raise ValueError(f"Source branch '{source_branch}' not found.")
        source_ref = refs[0]
        new_ref = GitRefUpdate(
            name=f"refs/heads/{branch_name}",
            old_object_id="0000000000000000000000000000000000000000",
            new_object_id=source_ref.object_id
        )
        self.client.update_refs(ref_updates=[new_ref], repository_id=repository_id, project=self.auth.project_name)

    @classmethod
    def _to_repository(cls, repo) -> Repository:
        return Repository(
            id=repo.id,
            source_id=repo.id,
            name=repo.name,
            git_url=repo.remote_url,
            project=cls._to_project(repo.project)
        )

    @staticmethod
    def _to_project(project) -> Project:
        return Project(
            name=project.name,
            id=project.id,
            source_id=project.id,
            description=project.description,
            url=project.url
        )
