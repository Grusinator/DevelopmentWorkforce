from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField


class Organization(models.Model):
    name = models.CharField(max_length=255)
    azure_devops_id = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255)
    azure_devops_id = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Repository(models.Model):
    name = models.CharField(max_length=255)
    azure_devops_id = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pat_token = models.CharField(max_length=128)


class AgentWorkPermit(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    repository_name = models.CharField(max_length=255)
    backlog_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.agent} - {self.repository_name} - {self.backlog_name}"
