import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from organization.models import Agent, Repository, Project
from organization.schemas import AgentModel
from organization.services.fetch_new_tasks import WorkItemFetcher
from src.ado_integrations.repos.ado_repos_models import RepositoryModel
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi
from src.ado_integrations.workitems.ado_workitem_models import WorkItem


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
    return Repository.objects.create(
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
def mock_api(mock_work_item):
    mock_api = MagicMock(spec=ADOWorkitemsWrapperApi)
    mock_api.list_work_items.return_value = [mock_work_item]
    return mock_api


@pytest.fixture
def work_item_fetcher(mock_api):
    return WorkItemFetcher(api=mock_api)


@pytest.mark.django_db
def test_fetch_new_workitems(client, work_item_fetcher, agent, repo, mock_work_item):
    with patch('organization.services.fetch_new_tasks.app.send_task') as mock_send_task:
        work_item_fetcher.fetch_new_workitems(agent, repo)

        agent_md = AgentModel.model_validate(agent)
        repo_md = RepositoryModel.model_validate(repo)

        mock_send_task.assert_called_once_with(
            'organization.tasks.execute_task',
            args=[agent_md.model_dump(), repo_md.model_dump(), mock_work_item.model_dump()]
        )
