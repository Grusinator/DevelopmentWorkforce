from django.db import models
from django.contrib.auth.models import User


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
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} for {self.agent}"


class AgentTask(models.Model):
    session = models.ForeignKey(AgentWorkSession, on_delete=models.CASCADE, related_name='tasks')
    ado_task_id = models.CharField(max_length=255)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'),
                                                      ('completed', 'Completed'), ('failed', 'Failed')],
                              default='pending')
    token_usage = models.IntegerField(default=0)

    def __str__(self):
        return f"Task {self.ado_task_id} for Session {self.session.id}"
