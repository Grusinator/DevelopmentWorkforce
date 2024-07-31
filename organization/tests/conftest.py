from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import User

from organization.models import Agent, Repository as RepositoryDb, Project

from organization.services.fetch_new_tasks import TaskFetcherAndScheduler
from src.devops_integrations.models import DevOpsSource
from src.devops_integrations.repos.ado_repos_models import Repository
from src.devops_integrations.workitems.ado_workitem_models import WorkItem
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi
from tests.test_devops_integrations.conftest import auth
from tests.test_devops_integrations.test_repos.conftest import *

__all__ = ["auth", "get_repository"]


@pytest.fixture
def user(db):
    return User.objects.create(username="test_user", email="test@example.com", password="password")


@pytest.fixture
def project(db):
    return Project.objects.create(name="Test Project", source_id="proj_123")


@pytest.fixture
def agent(db, user):
    return Agent.objects.create(
        user=user,
        pat="test_pat",
        status="idle",
        organization_name="Test Org",
        agent_user_name="test_user"
    )


@pytest.fixture
def repo(db, project):
    return RepositoryDb.objects.create(
        name="Test Repo",
        source_id="123456",
        project=project
    )


@pytest.fixture
def mock_work_item():
    return WorkItem(
        source_id=1,
        title="Test Work Item",
        state="New",
        description="This is a test work item",
        assigned_to="test_user",
        type="US"
    )


@pytest.fixture
def work_item_fetcher(agent, get_repository, mock_work_item):
    fetcher_and_scheduler = TaskFetcherAndScheduler(agent, get_repository, DevOpsSource.MOCK)
    fetcher_and_scheduler.workitems_api.work_items = [mock_work_item]
    return fetcher_and_scheduler
