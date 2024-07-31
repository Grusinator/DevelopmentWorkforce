from datetime import datetime

from organization.models import AgentTask, Agent, WorkItem
from src.base_task_updater import TaskUpdaterBase


class TaskUpdater(TaskUpdaterBase):
    def __init__(self, agent: Agent):
        self.agent = agent
        self.work_session = self.agent.active_work_session

    def start_agent_task(self, work_item_id=None, pull_request_id=None, status='active') -> object:
        work_item, _ = WorkItem.objects.get_or_create(
            work_item_source_id=work_item_id,
            defaults={'pull_request_source_id': pull_request_id, 'status': status}
        )

        agent_task = AgentTask.objects.create(
            session=self.agent.active_work_session,
            work_item=work_item
        )

        return agent_task

    def end_agent_task(self, agent_task: object, status=None, token_usage=None, pull_request_id=None):
        work_item = agent_task.work_item
        if status:
            work_item.status = status
        if pull_request_id:
            work_item.pull_request_source_id = pull_request_id
        work_item.save()

        agent_task.end_time = datetime.now()
        if token_usage is not None:
            agent_task.token_usage = token_usage
        agent_task.save()
