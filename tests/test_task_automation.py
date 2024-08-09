from pathlib import Path

import pytest

from organization.schemas import AgentModel
from organization.services.task_updater_hook import TaskUpdater
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
from src.local_development_session import LocalDevelopmentResult


@pytest.fixture
def mocked_local_dev_session(workspace_dir):
    session = MockDevSession(repo_dir=workspace_dir)
    return session


@pytest.fixture
def mocked_task_automation(work_item_model, agent_model, repository_model, workspace_dir):
    task_updater = MagicMock()
    task_automation = TaskAutomation(repository_model, agent_model, devops_source=DevOpsSource.MOCK,
                                     task_updater=task_updater)
    task_automation.devops_factory.mock_workitems_api.work_items.append(work_item_model)
    task_automation.git_manager = MagicMock()
    task_automation.dev_session = MockDevSession(repo_dir=workspace_dir)
    yield task_automation


class TestTaskAutomation:
    def test_task_automation_process(self, mocked_task_automation, work_item_model, repository_model, workspace_dir):
        mocked_task_automation.develop_on_task(work_item_model, repository_model)
        dummy_file_path = workspace_dir / "dummy_file.txt"
        assert dummy_file_path.exists()
        assert len(mocked_task_automation.pull_requests_api.pull_requests) == 1

    def test_pytest_parses_dummy_repo(self, workspace_dir_dummy_repo):
        run_pytest_in_workspace(workspace_dir_dummy_repo)
        struct = DirectoryStructure(workspace_dir_dummy_repo).get_formatted_directory_structure()
        print(struct)

    @pytest.mark.integration
    def test_update_pr_from_feedback(self, db, agent_in_db, get_repository, create_pull_request, create_work_item,
                                     ado_pull_requests_api, workspace_dir):
        comment_text = "This is a test feedback comment, i say ping, you say pong. PING!"
        repository_name = create_pull_request.repository.name
        ado_pull_requests_api.create_comment(repository_name, create_pull_request.id, comment_text)
        agent_model = AgentModel.model_validate(agent_in_db)
        task_automation = TaskAutomation(repo=get_repository, agent=agent_model, task_updater=TaskUpdater(agent_in_db),
                                         devops_source=DevOpsSource.ADO)
        task_automation.dev_session = MockDevSession(repo_dir=workspace_dir)
        task_automation.update_pr_from_feedback(create_pull_request, create_work_item)

    @pytest.mark.requires_llm
    def test_update_pr_from_feedback(self, mocked_task_automation, pull_request_model, work_item_model,
                                     comment_thread_model):
        mocked_task_automation.pull_requests_api: MockPullRequestsApi
        mocked_task_automation.pull_requests_api.create_comment = MagicMock()
        mocked_task_automation.pull_requests_api.pull_requests.append(pull_request_model)
        mocked_task_automation.workitems_api.work_items.append(work_item_model)
        mocked_task_automation.repos_api.repositories.append(pull_request_model.repository)
        mocked_task_automation.pull_requests_api.comment_threads.append(comment_thread_model)

        mocked_task_automation.update_pr_from_feedback(pull_request_model, work_item_model)
        mocked_task_automation.pull_requests_api.create_comment.assert_called_once()
        assert mocked_task_automation.pull_requests_api.comment_threads[0].comments[
                   -1].text == "Response to comment thread: 0"
