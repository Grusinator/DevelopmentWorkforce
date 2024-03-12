from development_workforce.ado_integrations.ado_repo import AdoRepo
import pytest


@pytest.fixture
def create_pull_request():
    repo = AdoRepo("test_repo")
    pull_request_id = repo.create_pull_request("feature-test")
    yield pull_request_id
    repo.abandon_pull_request(pull_request_id)


def test_approve_pull_request(create_pull_request):
    repo = AdoRepo("test_repo")
    repo.approve_pull_request(create_pull_request)


def test_reject_pull_request(create_pull_request):
    repo = AdoRepo("test_repo")
    repo.reject_pull_request(create_pull_request)


def test_abandon_pull_request(create_pull_request):
    repo = AdoRepo("test_repo")
    repo.abandon_pull_request(create_pull_request)


def test_merge_pull_request(create_pull_request):
    repo = AdoRepo("test_repo")
    repo.merge_pull_request(create_pull_request)


def test_write_comment(create_pull_request):
    repo = AdoRepo("test_repo")
    comment = "This is a test comment"
    repo.write_comment(create_pull_request, comment)


def test_list_pull_requests(create_pull_request):
    repo = AdoRepo("test_repo")
    prs = repo.list_pull_requests()
    assert prs["count"] == 1
    assert prs["value"][0]["pullRequestId"] == create_pull_request
