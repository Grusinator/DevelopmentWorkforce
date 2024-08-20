import pytest

from organization.schemas import AgentModel
from src.devops_integrations.models import DevOpsSource
from src.devops_integrations.pull_requests.mock_pull_requests_api import MockPullRequestsApi
from src.mock_local_development_session import MockDevSession
from src.task_automation import TaskAutomation
from src.util_tools.map_dir import DirectoryStructure
from tests.run_pytest_in_workspace import run_pytest_in_workspace


@pytest.fixture
def mocked_pull_requests_api(pull_request_model, comment_thread_model, repository_model):
    api = MockPullRequestsApi()
    return api


import pytest
from unittest.mock import MagicMock
from src.local_development_session import LocalDevelopmentSession


@pytest.fixture
def mocked_local_dev_session(workspace_dir):
    session = MockDevSession(repo_dir=workspace_dir)
    return session


@pytest.fixture
def task_automation_w_devops_mock(work_item_model, pull_request_model, agent_model, repository_model, workspace_dir,
                                  comment_thread_model):
    task_updater = MagicMock()
    task_automation = TaskAutomation(repository_model, agent_model, devops_source=DevOpsSource.MOCK,
                                     task_updater=task_updater)
    task_automation.pull_requests_api.pull_requests.append(pull_request_model)
    task_automation.workitems_api.work_items.append(work_item_model)
    task_automation.repos_api.repositories.append(repository_model)
    task_automation.pull_requests_api.comment_threads.append(comment_thread_model)
    task_automation.git_manager = MagicMock()
    task_automation.dev_session = MockDevSession(repo_dir=workspace_dir)
    yield task_automation


@pytest.fixture
def task_automation_all_mocked(workspace_dir, task_automation_w_devops_mock):
    task_automation_w_devops_mock.git_manager = MagicMock()
    task_automation_w_devops_mock.dev_session = MockDevSession(repo_dir=workspace_dir)
    yield task_automation_w_devops_mock


@pytest.fixture
def task_automation_w_ado(work_item_model, pull_request_model, agent_model, repository_model, workspace_dir):
    task_updater = MagicMock()
    task_automation = TaskAutomation(repository_model, agent_model, task_updater=task_updater,
                                     devops_source=DevOpsSource.ADO)

    task_automation.git_manager = MagicMock()
    yield task_automation


class TestTaskAutomation:
    def test_task_automation_process(self, task_automation_all_mocked, work_item_model, repository_model,
                                     workspace_dir):
        assert len(task_automation_all_mocked.pull_requests_api.pull_requests) == 1
        task_automation_all_mocked.develop_on_task(work_item_model, repository_model)
        dummy_file_path = workspace_dir / "dummy_file.txt"
        assert dummy_file_path.exists()
        assert len(task_automation_all_mocked.pull_requests_api.pull_requests) == 2

    def test_pytest_parses_dummy_repo(self, workspace_dir_dummy_repo):
        run_pytest_in_workspace(workspace_dir_dummy_repo)
        struct = DirectoryStructure(workspace_dir_dummy_repo).get_formatted_directory_structure()
        print(struct)

    @pytest.mark.integration
    def test_update_pr_from_feedback_integration(self, db, agent_in_db, get_repository, create_pull_request,
                                                 create_work_item, ado_pull_requests_api, workspace_dir):
        comment_text = "This is a test feedback comment"
        repository_name = create_pull_request.repository.name
        ado_pull_requests_api.create_comment(repository_name, create_pull_request.id, comment_text)
        agent_model = AgentModel.model_validate(agent_in_db)
        task_automation = TaskAutomation(repo=get_repository, agent=agent_model, devops_source=DevOpsSource.ADO)

        task_automation.dev_session = MockDevSession(repo_dir=workspace_dir)
        task_automation.update_pr_from_feedback(create_pull_request, create_work_item)
        comment_threads = task_automation.pull_requests_api.get_pull_request_comments(repository_name,
                                                                                      create_pull_request.id)
        assert len(comment_threads) == 1
        assert comment_threads[0].comments[-1].text == f"Response to comment thread: {comment_threads[0].id}"

    @pytest.mark.requires_llm
    def test_update_pr_from_feedback_w_llm(self, task_automation_w_devops_mock, pull_request_model, work_item_model,
                                           comment_thread_model):
        task_automation_w_devops_mock.dev_session = LocalDevelopmentSession()
        task_automation_w_devops_mock.update_pr_from_feedback(pull_request_model, work_item_model)

        comment_text = task_automation_w_devops_mock.pull_requests_api.comment_threads[0].comments[-1].text
        assert "pong" in comment_text
