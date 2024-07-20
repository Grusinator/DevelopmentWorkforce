# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PATTokenForm, AgentWorkPermitForm
from .models import Agent, AgentWorkPermit
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

@login_required
def input_pat_token(request):
    if request.method == 'POST':
        form = PATTokenForm(request.POST)
        if form.is_valid():
            pat_token = form.cleaned_data['pat_token']
            agent, created = Agent.objects.get_or_create(user=request.user)
            agent.pat_token = pat_token
            agent.save()
            return redirect('agent_work_permits')
    else:
        form = PATTokenForm()
    return render(request, 'input_pat_token.html', {'form': form})

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

@login_required
def fetch_projects_and_repos(request):
    agent = Agent.objects.get(user=request.user)
    pat_token = agent.pat_token

    credentials = BasicAuthentication('', pat_token)
    connection = Connection(base_url='https://dev.azure.com', creds=credentials)
    core_client = connection.clients.get_core_client()
    git_client = connection.clients.get_git_client()

    organizations = core_client.get_organizations()
    projects = []
    repositories = []

    for org in organizations.value:
        org_projects = core_client.get_projects(org.id)
        projects.extend(org_projects.value)
        for project in org_projects.value:
            repos = git_client.get_repositories(project.id)
            repositories.extend(repos.value)

    return render(request, 'list_projects_and_repos.html', {
        'projects': projects,
        'repositories': repositories
    })

