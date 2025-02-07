import os

import pytest
from django.contrib.auth.models import User

from organization.models import Project, Agent, AgentWorkSession, Repository, WorkItem
from organization.schemas import AgentModel
from organization.services.task_fetcher_and_scheduler import TaskFetcherAndScheduler
from src.devops_integrations.models import DevOpsSource
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.git_manager import GitManager


@pytest.fixture
def user_in_db(transactional_db):
    return User.objects.create(username="test_user", email="test@example.com", password="password")


@pytest.fixture
def project_in_db(transactional_db):
    proj_name = os.getenv("ADO_PROJECT_NAME")
    return Project.objects.create(name=proj_name, source_id="proj_123")


@pytest.fixture
def agent_in_db(transactional_db, user_in_db, agent_model):
    agent = Agent.objects.create(user=user_in_db, pat=agent_model.pat, status="working",
                                 organization_name=agent_model.organization_name,
                                 agent_user_name=agent_model.agent_user_name)
    agent_model.id = agent.id
    work_session = AgentWorkSession.objects.create(agent=agent)
    agent.active_work_session = work_session
    agent.save()
    return agent


@pytest.fixture
def repo_in_db(transactional_db, project_in_db):
    return Repository.objects.create(
        name=os.getenv("ADO_REPO_NAME"),
        source_id="123456",
        project=project_in_db
    )


@pytest.fixture
def git_manager(agent_model):
    return GitManager(pat=agent_model.pat)


@pytest.fixture
def work_item_model(agent_model):
    return WorkItemModel(
        source_id=1,
        title="Test Work Item",
        state="New",
        description="This is a test work item",
        assigned_to=agent_model.agent_user_name,
        type="US"
    )


@pytest.fixture
def work_item_in_db(work_item_model):
    return WorkItem.objects.create(source_id=work_item_model.source_id, title_id=work_item_model.title)


@pytest.fixture
def fetcher_and_scheduler(agent_in_db, agent_model, repository_model, work_item_model, pull_request_model):
    fetcher_and_scheduler = TaskFetcherAndScheduler(agent_model, repository_model, DevOpsSource.MOCK )
    fetcher_and_scheduler.workitems_api.work_items = [work_item_model]
    fetcher_and_scheduler.repos_api.repositories = [repository_model]
    fetcher_and_scheduler.pull_requests_api.pull_requests = []
    return fetcher_and_scheduler


@pytest.fixture
def agent_model():
    ado_org_name = os.getenv("ADO_ORGANIZATION_NAME")
    pat = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
    user_name = os.getenv("AI_USER_NAME")

    return AgentModel(id=1, organization_name=ado_org_name, pat=pat, agent_user_name=user_name, status="idle")
