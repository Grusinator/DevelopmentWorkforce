# views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from src.ado_integrations.repos.ado_repos_wrapper_api import ADOReposWrapperApi
from organization.forms import AgentForm, AgentRepoConnectionFormSet
from organization.models import Agent, Project, Repository, AgentRepoConnection
from loguru import logger

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from organization.forms import AgentRepoConnectionForm
from organization.models import AgentRepoConnection


@login_required
def sync_with_ado(request):
    agent, created = Agent.objects.get_or_create(user=request.user)
    api = ADOReposWrapperApi(agent.pat, agent.organization_name, None, None)
    projects = api.get_projects()

    for project in projects:
        project_obj, created = Project.objects.update_or_create(
            azure_devops_id=project.id,
            defaults={'name': project.name}
        )

        repositories = api.get_repositories(project.id)
        for repo in repositories:
            repo_obj, created = Repository.objects.update_or_create(
                azure_devops_id=repo.id,
                defaults={'name': repo.name, 'project': project_obj, "git_url": repo.url}
            )
            AgentRepoConnection.objects.get_or_create(
                agent=agent,
                repository=repo_obj,
                defaults={'enabled': False}
            )

    return redirect('display_repositories')


@login_required
def display_repositories(request):
    try:
        agent = Agent.objects.get(user=request.user)
        repositories = Repository.objects.all()
        connections = AgentRepoConnection.objects.filter(agent=agent)
        logger.debug(f"connections: {connections}")
    except Agent.DoesNotExist:
        agent = None
        repositories = []
        connections = AgentRepoConnection.objects.none()
        messages.info(request, "Please set up an agent by adding a PAT token.")

    if request.method == 'POST' and agent:
        formset = AgentRepoConnectionFormSet(request.POST, queryset=connections)
        if formset.is_valid():
            logger.debug(f"formset is valid")
            formset.save()
            return redirect('display_repositories')
        else:
            logger.debug(f"form has errors: {formset.errors}")
    else:
        formset = AgentRepoConnectionFormSet(queryset=connections)

    return render(request, 'repositories.html', {'formset': formset, 'repositories': repositories, 'agent': agent})


@login_required
def set_pat_token(request):
    agent, created = Agent.objects.get_or_create(user=request.user)
    logger.debug(f'Agent {agent} has pat token: {bool(agent.pat)}')

    if request.method == 'POST':
        form = AgentForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, 'PAT token updated successfully.')
            return redirect('display_repositories')
    else:
        form = AgentForm(instance=agent)

    return render(request, 'set_pat_token.html', {'form': form})


@login_required
def update_repository_connection(request, connection_id):
    connection = get_object_or_404(AgentRepoConnection, id=connection_id)

    if request.method == 'POST':
        form = AgentRepoConnectionForm(request.POST, instance=connection)
        if form.is_valid():
            form.save()
            return redirect('display_repositories')
    else:
        form = AgentRepoConnectionForm(instance=connection)

    return render(request, 'update_repository_connection.html', {'form': form})
