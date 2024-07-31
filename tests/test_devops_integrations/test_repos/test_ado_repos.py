import os

import pytest
from requests import HTTPError

from src.devops_integrations.repos.ado_repos_api import ADOReposApi
from src.devops_integrations.pull_requests.pull_request_models import CreatePullRequestInput


@pytest.mark.integration
class TestADOReposApiIntegration:

    def test_create_branch(self, ado_repos_api: ADOReposApi, get_repository):
        repository_id = get_repository.source_id
        source_branch = 'main'
        new_branch = 'test-branch'

        if not ado_repos_api.branch_exists(repository_id, source_branch):
            pytest.skip(f"Source branch '{source_branch}' does not exist.")

        ado_repos_api.create_branch(repository_id, new_branch, source_branch)
        assert ado_repos_api.branch_exists(repository_id, new_branch)

    def test_get_projects(self, ado_repos_api: ADOReposApi):
        projects = ado_repos_api.get_projects()

        assert len(projects) > 0
        for project in projects:
            assert isinstance(project.id, str)
            assert isinstance(project.name, str)
            assert isinstance(project.url, str)

    def test_get_repositories(self, ado_repos_api: ADOReposApi):
        projects = ado_repos_api.get_projects()

        if projects:
            project_id = projects[0].source_id
            repos = ado_repos_api.get_repositories(project_id)

            assert len(repos) > 0
            for repo in repos:
                assert isinstance(repo.source_id, str)
                assert isinstance(repo.name, str)
                assert isinstance(repo.git_url, str)
