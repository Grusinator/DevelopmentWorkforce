from django.utils import timezone

from development_workforce.celery import app
from organization.models import AgentWorkSession
from organization.services.task_fetcher_and_scheduler import EXECUTE_TASK_WORKITEM_NAME


def stop_work_session(agent):
    agent.status = 'idle'
    if agent.active_work_session:
        agent.active_work_session.end_time = timezone.now()
        agent.active_work_session.save()
        agent.active_work_session = None
        agent.save()
    # Stop all active tasks gracefully
    active_tasks = app.control.inspect().active() or dict()
    for worker, tasks in active_tasks.items():
        for task in tasks:
            if task['name'] == EXECUTE_TASK_WORKITEM_NAME and task['kwargs']['agent_id'] == agent.source_id:
                app.control.revoke(task['id'], terminate=True)


def start_work_session(agent):
    agent.status = 'working'
    work_session = AgentWorkSession.objects.create(agent=agent)
    agent.active_work_session = work_session
    agent.save()



