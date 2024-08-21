from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from organization.models import Agent, WorkItem, AgentTask
from loguru import logger


@login_required
def work_items(request):
    logger.debug("Loading work items view")

    # Get the agent associated with the current user
    agent = Agent.objects.get(user=request.user)

    # Fetch all work items associated with this agent via related tasks
    work_items = WorkItem.objects.filter(tasks__session__agent=agent).distinct()

    return render(request, 'work_items.html', {
        'agent': agent,
        'work_items': work_items,
    })