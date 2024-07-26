# views.py
from loguru import logger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi
from ..models import Agent, Repository
from ..services.services import stop_work_session, start_work_session
from ..services.fetch_new_tasks import WorkItemFetcher


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
            api = ADOWorkitemsWrapperApi(agent.pat, agent.organization_name, repo.project.name)
            wf = WorkItemFetcher(api)  # TODO design these classes without user info, and parse it along.
            # TODO use django_injector
            wf.fetch_new_workitems(agent, repo)
        elif 'stop' in request.POST:
            stop_work_session(agent)
        return redirect('agent_status')

    return render(request, 'agent_status.html', {'agent': agent, 'repositories': repositories})
