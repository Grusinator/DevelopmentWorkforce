import os
from urllib.error import HTTPError

import pytest
from azure.devops.exceptions import AzureDevOpsServiceError

from src.devops_integrations.models import ProjectAuthenticationModel
from src.devops_integrations.pull_requests.ado_pull_requests_api import ADOPullRequestsApi
from src.devops_integrations.pull_requests.pull_request_models import CreatePullRequestInputModel

from src.devops_integrations.repos.ado_repos_api import ADOReposApi
from src.devops_integrations.workitems.ado_workitem_models import CreateWorkItemInputModel
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi


@pytest.fixture
def ado_workitems_api(auth_model) -> ADOWorkitemsApi:
    return ADOWorkitemsApi(auth_model)


@pytest.fixture
def create_work_item(ado_workitems_api: ADOWorkitemsApi, agent_model):
    work_item_input = CreateWorkItemInputModel(title="Test Work Item", description="This is a test work item",
                                               type="Task", assigned_to=agent_model.agent_user_name, state="New")
    work_item = ado_workitems_api.create_work_item(work_item_input)
    yield ado_workitems_api.get_work_item(work_item.source_id)
    try:
        ado_workitems_api.delete_work_item(work_item.source_id)
    except AzureDevOpsServiceError as e:
        if "does not exist" not in str(e):
            raise e


@pytest.fixture
def ado_repos_api(auth_model) -> ADOReposApi:
    return ADOReposApi(auth_model)


@pytest.fixture
def get_repository(auth_model, ado_repos_api: ADOReposApi):
    name = os.getenv("ADO_REPO_NAME")
    return ado_repos_api.get_repository(name)


@pytest.fixture
def ado_pull_requests_api(auth_model: ProjectAuthenticationModel) -> ADOPullRequestsApi:
    return ADOPullRequestsApi(auth_model)


@pytest.fixture
def mock_create_pull_request():
    return CreatePullRequestInputModel(title="Test Pull Request", description="This is a test pull request",
                                       source_branch="feature-branch",
                                       target_branch="main")


@pytest.fixture
def create_pull_request(ado_pull_requests_api, mock_create_pull_request, get_repository):
    pr = ado_pull_requests_api.create_pull_request(get_repository.name, mock_create_pull_request)
    yield pr
    if ado_pull_requests_api.get_pull_request(get_repository.source_id, pr.id).status != "abandoned":
        try:
            ado_pull_requests_api.abandon_pull_request(get_repository.name, pr.id)
        except AzureDevOpsServiceError as e:
            if "does not exist" not in str(e):
                raise e


@pytest.fixture
def no_active_pull_request_for_feature_branch(ado_pull_requests_api: ADOPullRequestsApi, setup_feature_branch,
                                              get_repository):
    prs = ado_pull_requests_api.list_pull_requests(get_repository.source_id)
    open_pr = next((pr for pr in prs if pr.title == "Create Test PR" and pr.status == 'active'), None)

    if open_pr:
        ado_pull_requests_api.abandon_pull_request(get_repository.name, open_pr.id)


@pytest.fixture
def setup_main_branch(ado_pull_requests_api: ADOPullRequestsApi, ado_repos_api: ADOReposApi, get_repository):
    main_branch = 'main'

    if not ado_repos_api.branch_exists(get_repository.source_id, main_branch):
        pytest.skip(f"Main branch '{main_branch}' does not exist.")


@pytest.fixture
def setup_feature_branch(ado_pull_requests_api: ADOPullRequestsApi, ado_repos_api, setup_main_branch, get_repository):
    feature_branch = 'feature-branch'

    if not ado_repos_api.branch_exists(get_repository.source_id, feature_branch):
        ado_repos_api.create_branch(get_repository.source_id, feature_branch, 'main')


@pytest.fixture
def open_pull_request(ado_pull_requests_api: ADOPullRequestsApi, setup_feature_branch, get_repository):
    pr_input = CreatePullRequestInputModel(
        source_branch="feature-branch",
        target_branch="main",
        title="Create Test PR",
        description="Test PR Description"
    )

    prs = ado_pull_requests_api.list_pull_requests(get_repository.source_id)
    open_pr = next((pr for pr in prs if pr.title == pr_input.title and pr.status == 'active'), None)

    pr = open_pr if open_pr else ado_pull_requests_api.create_pull_request(get_repository.source_id, pr_input)
    yield pr
    try:
        ado_pull_requests_api.abandon_pull_request(get_repository.name, pr.id)
    except HTTPError:
        pass


@pytest.fixture
def run_build(ado_pull_requests_api: ADOPullRequestsApi, open_pull_request):
    pr_id = open_pull_request.id
    build_id = ado_pull_requests_api.run_build(pr_id)
    yield build_id


@pytest.fixture
def add_pull_request_comment(ado_pull_requests_api: ADOPullRequestsApi, open_pull_request, get_repository):
    pr_id = open_pull_request.id
    comment_content = "This is a test comment."
    comment_id = ado_pull_requests_api.create_comment(get_repository.name, pr_id, comment_content)
    yield comment_id
