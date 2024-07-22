from django.contrib import admin
from .models import Project, Repository, Agent, AgentRepoConnection

admin.site.register(Project)
admin.site.register(Repository)
admin.site.register(Agent)
admin.site.register(AgentRepoConnection)

