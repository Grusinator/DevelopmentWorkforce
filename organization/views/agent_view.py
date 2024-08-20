# views.py
from loguru import logger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from src.devops_integrations.repos.ado_repos_models import RepositoryModel
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi
from ..models import Agent, Repository, AgentWorkSession, AgentTask, WorkItem
from ..schemas import AgentModel
from ..services.services import stop_work_session, start_work_session
from ..services.task_fetcher_and_scheduler import TaskFetcherAndScheduler


@login_required
def agent_status(request):
    logger.debug("test")
    agent = Agent.objects.get(user=request.user)
    repositories = Repository.objects.filter(agentrepoconnection__agent=agent, agentrepoconnection__enabled=True)
    logger.debug(f"repos: {repositories}")

    if request.method == 'POST':
        selected_repo = request.POST.get('repository')
        repo = Repository.objects.get(id=selected_repo)

        if 'start' in request.POST:
            start_work_session(agent)
            _fetch_new_tasks(agent, repo)
        elif 'stop' in request.POST:
            stop_work_session(agent)
        return redirect('agent_status')

    work_sessions = AgentWorkSession.objects.filter(agent=agent)

    return render(request, 'agent_status.html',
                  {'agent': agent, 'repositories': repositories, 'work_sessions': work_sessions})


def _fetch_new_tasks(agent, repo):
    agent_md = AgentModel.model_validate(agent)
    repo_md = RepositoryModel.model_validate(repo)
    wf = TaskFetcherAndScheduler(agent_md, repo_md)
    wf.fetch_new_workitems(agent_md, repo_md)
    wf.fetch_pull_requests_waiting_for_author(agent_md, repo_md)
