import os
from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import User

from organization.models import Agent, Repository as RepositoryDb, Project
from organization.schemas import AgentModel

from organization.services.fetch_new_tasks import TaskFetcherAndScheduler
from src.devops_integrations.models import DevOpsSource
from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi
from tests.test_devops_integrations.conftest import auth
from tests.test_devops_integrations.test_repos.conftest import *

__all__ = ["auth", "get_repository"]


@pytest.fixture
def user(db):
    return User.objects.create(username="test_user", email="test@example.com", password="password")


@pytest.fixture
def project_in_db(db):
    proj_name = os.getenv("ADO_PROJECT_NAME")
    return Project.objects.create(name=proj_name, source_id="proj_123")


@pytest.fixture
def agent_in_db(db, user):
    return Agent.objects.create(
        user=user,
        pat="test_pat",
        status="idle",
        organization_name="Test Org",
        agent_user_name="test_user"
    )



@pytest.fixture
def repo_in_db(db, project_in_db):
    return RepositoryDb.objects.create(
        name=os.getenv("ADO_REPO_NAME"),
        source_id="123456",
        project=project_in_db
    )


@pytest.fixture
def mock_work_item():
    return WorkItemModel(
        source_id=1,
        title="Test Work Item",
        state="New",
        description="This is a test work item",
        assigned_to="test_user",
        type="US"
    )


@pytest.fixture
def work_item_fetcher(mock_agent, get_repository, mock_work_item):
    fetcher_and_scheduler = TaskFetcherAndScheduler(mock_agent, get_repository, DevOpsSource.MOCK)
    fetcher_and_scheduler.workitems_api.work_items = [mock_work_item]
    return fetcher_and_scheduler


@pytest.fixture
def mock_agent():
    ado_org_name = os.getenv("ADO_ORGANIZATION_NAME")
    pat = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
    user_name = os.getenv("AI_USER_NAME")

    return AgentModel(id=1, organization_name=ado_org_name, pat=pat, agent_user_name=user_name, status="idle")
