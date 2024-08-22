from enum import Enum

from django.db import models
from django.contrib.auth.models import User

from src.devops_integrations.workitems.ado_workitem_models import WorkItemStateEnum, WorkItemModel



class Project(models.Model):
    id = models.AutoField(primary_key=True)
    source_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    # url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class Repository(models.Model):
    id = models.AutoField(primary_key=True)
    source_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    git_url = models.URLField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Agent(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pat = models.CharField(max_length=128)
    status = models.CharField(max_length=50, choices=[('idle', 'Idle'), ('working', 'Working')], default='idle')
    organization_name = models.CharField(max_length=128)
    agent_user_name = models.CharField(max_length=255)
    active_work_session = models.ForeignKey('AgentWorkSession', on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='active_agent')

    def __str__(self):
        return self.user.username


class AgentRepoConnection(models.Model):
    id = models.AutoField(primary_key=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.agent} - {self.repository}"


class AgentWorkSession(models.Model):
    """an agent is working continuously on a session. until stopped"""
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} for {self.agent}"


class WorkItem(models.Model):
    id = models.AutoField(primary_key=True)
    source_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    pull_request_source_id = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(
        max_length=50,
        choices=WorkItemStateEnum.choices(),
        default=WorkItemStateEnum.PENDING,
    )

    @classmethod
    def from_pydantic(cls, work_item: WorkItemModel):
        return cls(
            source_id=work_item.source_id,
            pull_request_source_id=work_item.pull_request_source_id,
            state=work_item.state
        )

class TaskStatusEnum(str, Enum):
    PENDING = 'pending'  # waiting to be picked up by an agent
    COMPLETED = 'completed'
    IN_PROGRESS = 'in_progress'  # has been developed on but pr not completed
    FAILED = 'failed'

    @classmethod
    def choices(cls):
        return [(key.value, key.name.replace("_", " ").title()) for key in cls]

class AgentTask(models.Model):
    """every time an agent does a job its a task. an iteration of a crewai session.
    There can be many agent tasks (work item iteration) on each work item,
    say for example one for each pull request review iteration"""

    id = models.AutoField(primary_key=True)
    tag = models.CharField(max_length=50, null=True, blank=True, choices=[('DEV', 'Development'), ('PR', 'Pull Request')])
    session = models.ForeignKey(AgentWorkSession, on_delete=models.CASCADE, related_name='tasks')
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=50, choices=TaskStatusEnum.choices(), default=TaskStatusEnum.PENDING)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    token_usage = models.IntegerField(default=0)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)

    def __str__(self):
        return f"Task {self.id}, wo: {self.work_item.title} for Session {self.session.start_time}"
