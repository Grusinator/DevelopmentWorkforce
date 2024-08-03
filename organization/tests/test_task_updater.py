import pytest

from organization.services.task_updater_hook import TaskUpdater


@pytest.mark.django_db
class TestTaskUpdater:


    def test_get_or_create_agent_task(self, agent_in_db):
        agent = agent_in_db
        task_updater = TaskUpdater(agent)

        # Test creating a new agent task
        agent_task = task_updater.start_agent_task(work_item_id="123", pull_request_id="456", status="pending")
        assert agent_task is not None
        assert agent_task.work_item.work_item_source_id == "123"
        assert agent_task.work_item.pull_request_source_id == "456"
        assert agent_task.work_item.status == "pending"

        # Test getting a new agent task
        agent_task_existing = task_updater.start_agent_task(work_item_id="123", pull_request_id="456",
                                                            status="pending")
        assert agent_task.id != agent_task_existing.id

    def test_update_agent_task(self, agent_in_db):
        agent = agent_in_db
        task_updater = TaskUpdater(agent)

        # Create a new agent task
        agent_task = task_updater.start_agent_task(work_item_id="123", pull_request_id="456", status="pending")

        # Update the agent task
        task_updater.end_agent_task(agent_task, status="completed", token_usage=100,
                                    pull_request_id="789")

        agent_task.refresh_from_db()
        assert agent_task.work_item.status == "completed"
        assert agent_task.end_time is not None
        assert agent_task.token_usage == 100
        assert agent_task.work_item.pull_request_source_id == "789"
