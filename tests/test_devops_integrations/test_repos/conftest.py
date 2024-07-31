import os

import pytest

from src.devops_integrations.repos.ado_repos_api import ADOReposApi


@pytest.fixture
def ado_repos_api(auth) -> ADOReposApi:
    return ADOReposApi(auth)


@pytest.fixture
def get_repository(auth, ado_repos_api: ADOReposApi):
    name = os.getenv("ADO_REPO_NAME")
    return ado_repos_api.get_repository(name)
