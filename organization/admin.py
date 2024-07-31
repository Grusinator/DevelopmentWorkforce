from django.contrib import admin
from .models import Project, Repository, Agent, AgentRepoConnection, AgentWorkSession, AgentTask, WorkItem

admin.site.register(Project)
admin.site.register(Repository)
admin.site.register(Agent)
admin.site.register(AgentRepoConnection)
admin.site.register(AgentTask)
admin.site.register(AgentWorkSession)
admin.site.register(WorkItem)


