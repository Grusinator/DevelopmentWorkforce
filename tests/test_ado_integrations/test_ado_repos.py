import pytest
from src.ado_integrations.repos.ado_repos_wrapper_api import ADOReposWrapperApi
from src.ado_integrations.repos.ado_repos_models import CreatePullRequestInput

@pytest.mark.integration
class TestADOReposApiIntegration:

    @pytest.fixture
    def api(self) -> ADOReposWrapperApi:
        return ADOReposWrapperApi()

    @pytest.fixture
    def setup_main_branch(self, api: ADOReposWrapperApi):
        repository_id = api.get_repository_id()
        main_branch = 'main'

        if not api.branch_exists(repository_id, main_branch):
            pytest.skip(f"Main branch '{main_branch}' does not exist.")

    @pytest.fixture
    def setup_feature_branch(self, api: ADOReposWrapperApi, setup_main_branch):
        repository_id = api.get_repository_id()
        feature_branch = 'feature-branch'

        if not api.branch_exists(repository_id, feature_branch):
            api.create_branch(repository_id, feature_branch, 'main')

    @pytest.fixture
    def open_pull_request(self, api: ADOReposWrapperApi, setup_feature_branch):
        pr_input = CreatePullRequestInput(
            source_branch="feature-branch",
            target_branch="main",
            title="Create Test PR",
            description="Test PR Description"
        )

        prs = api.list_pull_requests(api.get_repository_id())
        open_pr = next((pr for pr in prs if pr.title == pr_input.title and pr.status == 'active'), None)

        pr_id = open_pr.id if open_pr else api.create_pull_request(pr_input)
        yield pr_id
        api.abandon_pull_request(pr_id)

    @pytest.fixture
    def run_build(self, api: ADOReposWrapperApi, open_pull_request):
        pr_id = open_pull_request
        build_id = api.run_build(pr_id)
        yield build_id

    @pytest.fixture
    def add_pull_request_comment(self, api: ADOReposWrapperApi, open_pull_request):
        pr_id = open_pull_request
        comment_content = "This is a test comment."
        comment_id = api.add_pull_request_comment(pr_id, comment_content)
        yield comment_id

    def test_create_branch(self, api: ADOReposWrapperApi):
        repository_id = api.get_repository_id()
        source_branch = 'main'
        new_branch = 'test-branch'

        if not api.branch_exists(repository_id, source_branch):
            pytest.skip(f"Source branch '{source_branch}' does not exist.")

        api.create_branch(repository_id, new_branch, source_branch)
        assert api.branch_exists(repository_id, new_branch)

    @pytest.fixture
    def no_active_pull_request_for_feature_branch(self, api: ADOReposWrapperApi, setup_feature_branch):
        prs = api.list_pull_requests(api.get_repository_id())
        open_pr = next((pr for pr in prs if pr.title == "Create Test PR" and pr.status == 'active'), None)

        if open_pr:
            api.abandon_pull_request(open_pr.id)

    def test_create_pull_request(self, api: ADOReposWrapperApi, no_active_pull_request_for_feature_branch):
        pr_input = CreatePullRequestInput(
            source_branch="feature-branch",
            target_branch="main",
            title="Create Test PR",
            description="Test PR Description"
        )
        pr_id = api.create_pull_request(pr_input)
        assert isinstance(pr_id, int)
        api.abandon_pull_request(pr_id)

    def test_get_pull_request(self, api: ADOReposWrapperApi, open_pull_request):
        pr_id = open_pull_request
        pr_details = api.get_pull_request(pr_id)
        assert pr_details.id == pr_id
        api.abandon_pull_request(pr_id)

    def test_update_pull_request_description(self, api: ADOReposWrapperApi, open_pull_request):
        pr_id = open_pull_request
        new_description = "Updated PR Description"
        api.update_pull_request_description(pr_id, new_description)
        updated_pr = api.get_pull_request(pr_id)
        assert updated_pr.description == new_description

    def test_list_pull_requests(self, api: ADOReposWrapperApi, setup_feature_branch):
        pr_list = api.list_pull_requests(api.get_repository_id())
        assert isinstance(pr_list, list)

    @pytest.mark.skip("not working")
    def test_complete_pull_request(self, api: ADOReposWrapperApi, open_pull_request):
        pr_id = open_pull_request
        api.complete_pull_request(pr_id)
        completed_pr = api.get_pull_request(pr_id)
        assert completed_pr.status == 'completed'

    @pytest.mark.skip("not working")
    def test_abandon_pull_request(self, api: ADOReposWrapperApi, open_pull_request):
        pr_id = open_pull_request
        api.abandon_pull_request(pr_id)
        abandoned_pr = api.get_pull_request(pr_id)
        assert abandoned_pr.status == 'abandoned'


    def test_add_pull_request_comment(self, api: ADOReposWrapperApi, open_pull_request):
        pr_id = open_pull_request
        comment_content = "This is a test comment."
        comment_id = api.add_pull_request_comment(pr_id, comment_content)
        assert isinstance(comment_id, int)

    def test_get_pull_request_comments(self, api: ADOReposWrapperApi, open_pull_request, add_pull_request_comment):
        pr_id = open_pull_request
        comments = api.get_pull_request_comments(pr_id)
        assert isinstance(comments, list)
        assert len(comments) == 1

    def test_get_build_status(self, api: ADOReposWrapperApi, open_pull_request, run_build):
        pr_id = open_pull_request
        status = api.get_build_status(pr_id)
        assert status in ['succeeded', 'failed', 'canceled', 'inProgress']


    @pytest.mark.integration
    def test_get_projects(self):
        api = ADOReposWrapperApi()
        projects = api.get_projects()

        assert len(projects) > 0
        for project in projects:
            assert isinstance(project.id, str)
            assert isinstance(project.name, str)
            assert isinstance(project.url, str)

    # Integration test for querying existing repositories within a project
    @pytest.mark.integration
    def test_get_repositories(self, api):
        projects = api.get_projects()

        if projects:
            project_id = projects[0].id
            repos = api.get_repositories(project_id)

            assert len(repos) > 0
            for repo in repos:
                assert isinstance(repo.id, str)
                assert isinstance(repo.name, str)
                assert isinstance(repo.url, str)
