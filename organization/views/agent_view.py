# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from loguru import logger

from development_workforce.celery import app, debug_task
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi
from src.task_automation import TaskAutomation
from ..models import Agent, Repository, AgentRepoConnection
from ..tasks import execute_task

@login_required
def agent_status(request):
    logger.debug("test")
    debug_task.delay()
    agent = Agent.objects.get(user=request.user)
    repositories = Repository.objects.filter(agentrepoconnection__agent=agent, agentrepoconnection__enabled=True)
    logger.debug(f"repos: {repositories}")

    if request.method == 'POST':
        selected_repo = request.POST.get('repository')
        repo = Repository.objects.get(id=selected_repo)

        if 'start' in request.POST:
            agent.status = 'working'
            agent.save()
            # Create Celery tasks for each new work item
            work_items_api = ADOWorkitemsWrapperApi(agent.pat, agent.organization_name, repo.project.name)
            new_tasks = work_items_api.list_work_items(assigned_to=agent.agent_user_name, state="New")
            for task in new_tasks:
                logger.debug(f"task started: {task}")
                execute_task.delay(repo.git_url, repo.name, agent.organization_name, repo.project.name, agent.pat, agent.agent_user_name, task.model_dump())
        elif 'stop' in request.POST:
            agent.status = 'idle'
            agent.save()
            # Stop all active tasks
            active_tasks = app.control.inspect().active() or dict()
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    if task['name'] == 'execute_task':
                        app.control.revoke(task['id'], terminate=True)
        return redirect('agent_status')

    return render(request, 'agent_status.html', {'agent': agent, 'repositories': repositories})
