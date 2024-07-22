# views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from src.ado_integrations.repos.ado_repos_wrapper_api import ADOReposWrapperApi
from .forms import AgentWorkPermitForm, AgentForm
from .models import Agent, AgentWorkPermit, Project, Repository
from loguru import logger


@login_required
def sync_with_ado(request):
    api = ADOReposWrapperApi()
    projects = api.get_projects()

    for project in projects:
        project_obj, created = Project.objects.update_or_create(
            azure_devops_id=project.id,
            defaults={'name': project.name}
        )

        repositories = api.get_repositories(project.id)
        for repo in repositories:
            Repository.objects.update_or_create(
                azure_devops_id=repo.id,
                defaults={'name': repo.name, 'project': project_obj}
            )

    return redirect('projects')


@login_required
def display_projects(request):
    projects = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects})


@login_required
def set_pat_token(request):
    agent, created = Agent.objects.get_or_create(user=request.user)
    logger.debug(f'Agent {agent} has pat token: {bool(agent.pat_token)}')

    if request.method == 'POST':
        form = AgentForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, 'PAT token updated successfully.')
            return redirect('agent_work_permits')
    else:
        form = AgentForm(instance=agent)

    return render(request, 'set_pat_token.html', {'form': form})

@login_required
def agent_work_permits(request):
    agent = Agent.objects.get(user=request.user)
    if request.method == 'POST':
        form = AgentWorkPermitForm(request.POST)
        if form.is_valid():
            work_permit = form.save(commit=False)
            work_permit.agent = agent
            work_permit.save()
            return redirect('list_work_permits')
    else:
        form = AgentWorkPermitForm()
    return render(request, 'agent_work_permits.html', {'form': form})

@login_required
def list_work_permits(request):
    agent = Agent.objects.get(user=request.user)
    work_permits = AgentWorkPermit.objects.filter(agent=agent)
    return render(request, 'list_work_permits.html', {'work_permits': work_permits})
