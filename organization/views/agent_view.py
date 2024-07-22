from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Agent


@login_required
def start_agent(request):
    agent = get_object_or_404(Agent, user=request.user)
    if agent.status != 'working':
        # Here you would call the method to start the agent working
        agent.status = 'working'
        agent.ado_task_id = '12345'  # Example task ID
        agent.save()
        messages.success(request, 'Agent started working.')
    else:
        messages.info(request, 'Agent is already working.')
    return redirect('agent_status')


@login_required
def stop_agent(request):
    agent = get_object_or_404(Agent, user=request.user)
    if agent.status == 'working':
        # Here you would call the method to stop the agent working
        agent.status = 'idle'
        agent.ado_task_id = None
        agent.save()
        messages.success(request, 'Agent stopped working.')
    else:
        messages.info(request, 'Agent is not currently working.')
    return redirect('agent_status')


@login_required
def agent_status(request):
    agent = get_object_or_404(Agent, user=request.user)
    return render(request, 'agent_status.html', {'agent': agent})
