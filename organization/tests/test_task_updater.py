import pytest
from django.utils.timezone import now
from organization.models import Agent, AgentWorkSession, WorkItem, AgentTask
from organization.services.task_updater_hook import TaskUpdater


@pytest.mark.django_db
class TestTaskUpdater:
    @pytest.fixture
    def setup_agent(self):
        agent = Agent.objects.create(name="Test Agent", status="working")
        work_session = AgentWorkSession.objects.create(agent=agent, status="active")
        agent.active_work_session = work_session
        agent.save()
        return agent

    def test_get_or_create_agent_task(self, setup_agent):
        agent = setup_agent
        task_updater = TaskUpdater(agent)

        # Test creating a new agent task
        agent_task = task_updater.start_agent_task(work_item_id="123", pull_request_id="456", status="pending")
        assert agent_task is not None
        assert agent_task.work_item.work_item_source_id == "123"
        assert agent_task.work_item.pull_request_source_id == "456"
        assert agent_task.status == "pending"

        # Test getting the existing agent task
        agent_task_existing = task_updater.start_agent_task(work_item_id="123", pull_request_id="456",
                                                            status="pending")
        assert agent_task.id == agent_task_existing.id

    def test_update_agent_task(self, setup_agent):
        agent = setup_agent
        task_updater = TaskUpdater(agent)

        # Create a new agent task
        agent_task = task_updater.start_agent_task(work_item_id="123", pull_request_id="456", status="pending")

        # Update the agent task
        task_updater.end_agent_task(agent_task, status="completed", token_usage=100,
                                    pull_request_id="789")

        agent_task.refresh_from_db()
        assert agent_task.status == "completed"
        assert agent_task.end_time is not None
        assert agent_task.token_usage == 100
        assert agent_task.work_item.pull_request_source_id == "789"
