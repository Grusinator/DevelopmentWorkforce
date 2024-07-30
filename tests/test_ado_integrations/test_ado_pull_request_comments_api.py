import os
import pytest
from azure.devops.exceptions import AzureDevOpsServiceError

from src.ado_integrations.repos.ado_repos_wrapper_api import ADOReposWrapperApi
from src.ado_integrations.repos.ado_repos_models import CreatePullRequestInput
from src.ado_integrations.workitems.ado_pull_request_comments_api import ADOPullRequestCommentsApi

ASSIGNED_TO = os.getenv("AI_USER_NAME")


@pytest.mark.integration
class TestADOPullRequestCommentsApiIntegration:

    @pytest.fixture
    def repos_api(self) -> ADOReposWrapperApi:
        pat = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
        ado_org_name = os.getenv("ADO_ORGANIZATION_NAME")
        project_name = os.getenv("ADO_PROJECT_NAME")
        repo_name = os.getenv("ADO_REPO_NAME")
        return ADOReposWrapperApi(pat, ado_org_name, project_name, repo_name)

    @pytest.fixture
    def comments_api(self) -> ADOPullRequestCommentsApi:
        pat = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
        ado_org_name = os.getenv("ADO_ORGANIZATION_NAME")
        project_name = os.getenv("ADO_PROJECT_NAME")
        repo_name = os.getenv("ADO_REPO_NAME")
        return ADOPullRequestCommentsApi(pat, ado_org_name, project_name, repo_name)

    @pytest.fixture
    def create_pull_request(self, repos_api: ADOReposWrapperApi):
        pr_input = CreatePullRequestInput(
            title="Test Pull Request",
            description="This is a test pull request",
            source_branch="feature-branch",
            target_branch="main"
        )
        pr_id = repos_api.create_pull_request(pr_input)
        yield pr_id
        try:
            repos_api.abandon_pull_request(pr_id)
        except AzureDevOpsServiceError as e:
            if "does not exist" not in str(e):
                raise e

    def test_add_and_list_comments(self, comments_api: ADOPullRequestCommentsApi, create_pull_request):
        pull_request_id = create_pull_request
        comment_text = "This is a test comment on a pull request."

        created_comment = comments_api.create_comment(pull_request_id, comment_text)
        comment_threads = comments_api.list_comments(pull_request_id)

        assert any(comment.text == comment_text for thread in comment_threads for comment in thread.comments)
        assert created_comment.text == comment_text

    def test_add_and_list_multiple_comments_and_threads(self, comments_api: ADOPullRequestCommentsApi, create_pull_request):
        pull_request_id = create_pull_request
        comment_texts = ["This is the first test comment.", "This is the second test comment.", "This is the third test comment."]

        for text in comment_texts:
            comments_api.create_comment(pull_request_id, text)

        comment_threads = comments_api.list_comments(pull_request_id)

        for text in comment_texts:
            assert any(comment.text == text for thread in comment_threads for comment in thread.comments)
