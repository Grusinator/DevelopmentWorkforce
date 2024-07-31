import pytest

from src.devops_integrations.pull_requests.ado_pull_requests_api import ADOPullRequestsApi


@pytest.mark.integration
class TestADOPullRequestsApi:

    def test_create_pull_request(self, ado_pull_requests_api: ADOPullRequestsApi,
                                 no_active_pull_request_for_feature_branch,
                                 mock_create_pull_request, get_repository):
        pr_id = ado_pull_requests_api.create_pull_request(get_repository.name, mock_create_pull_request)
        assert isinstance(pr_id, int)

    def test_get_pull_request(self, ado_pull_requests_api: ADOPullRequestsApi, create_pull_request,
                              mock_create_pull_request, get_repository):
        pr_id = create_pull_request
        pr_details = ado_pull_requests_api.get_pull_request(get_repository.source_id, pr_id)
        assert pr_details.id == pr_id

    def test_list_pull_requests(self, ado_pull_requests_api: ADOPullRequestsApi, setup_feature_branch,
                                mock_create_pull_request, get_repository):
        pr_list = ado_pull_requests_api.list_pull_requests(get_repository.name)
        assert isinstance(pr_list, list)

    def test_approve_pull_request(self, ado_pull_requests_api: ADOPullRequestsApi, create_pull_request,
                                  mock_create_pull_request, get_repository):
        pr_id = create_pull_request
        ado_pull_requests_api.approve_pull_request(get_repository.name, pr_id)
        completed_pr = ado_pull_requests_api.get_pull_request(get_repository.source_id, pr_id)
        assert completed_pr.status == 'active'

    def test_abandon_pull_request(self, ado_pull_requests_api: ADOPullRequestsApi, create_pull_request,
                                  mock_create_pull_request, get_repository):
        pr_id = create_pull_request
        ado_pull_requests_api.abandon_pull_request(get_repository.name, pr_id)
        abandoned_pr = ado_pull_requests_api.get_pull_request(get_repository.source_id, pr_id)
        assert abandoned_pr.status == 'abandoned'

    def test_add_pull_request_comment(self, ado_pull_requests_api: ADOPullRequestsApi, create_pull_request,
                                      mock_create_pull_request, get_repository):
        pr_id = create_pull_request
        comment_content = "This is a test comment."
        comment_id = ado_pull_requests_api.add_pull_request_comment(get_repository.name, pr_id, comment_content)
        assert isinstance(comment_id, int)

    def test_get_pull_request_comments(self, ado_pull_requests_api: ADOPullRequestsApi, create_pull_request,
                                       add_pull_request_comment,
                                       mock_create_pull_request, get_repository):
        pr_id = create_pull_request
        comments = ado_pull_requests_api.get_pull_request_comments(get_repository.name, pr_id)
        assert isinstance(comments, list)
        assert len(comments) == 1

    def test_add_and_list_comments(self, ado_pull_requests_api: ADOPullRequestsApi, create_pull_request,
                                   mock_create_pull_request, get_repository):
        pull_request_id = create_pull_request
        comment_text = "This is a test comment on a pull request."

        created_comment = ado_pull_requests_api.add_pull_request_comment(get_repository.name, pull_request_id,
                                                                         comment_text)
        comment_threads = ado_pull_requests_api.get_pull_request_comments(get_repository.name, pull_request_id)

        assert any(comment.text == comment_text for thread in comment_threads for comment in thread.comments)

    def test_add_and_list_multiple_comments_and_threads(self, ado_pull_requests_api: ADOPullRequestsApi,
                                                        create_pull_request,
                                                        mock_create_pull_request, get_repository):
        pull_request_id = create_pull_request
        comment_texts = ["This is the first test comment.", "This is the second test comment.",
                         "This is the third test comment."]

        for text in comment_texts:
            ado_pull_requests_api.add_pull_request_comment(get_repository.name, pull_request_id, text)

        comment_threads = ado_pull_requests_api.get_pull_request_comments(get_repository.name, pull_request_id)

        for text in comment_texts:
            assert any(comment.text == text for thread in comment_threads for comment in thread.comments)
