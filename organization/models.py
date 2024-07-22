from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    azure_devops_id = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Repository(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    azure_devops_id = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Agent(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # ms_user_name = models.CharField(max_length=255)
    pat_token = models.CharField(max_length=128)

    def __str__(self):
        return self.user.username


class AgentRepoConnection(models.Model):
    id = models.AutoField(primary_key=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.agent} - {self.repository}"
