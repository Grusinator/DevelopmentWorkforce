from django.db import models
from django.contrib.auth.models import User
from pgvector.django.models import VectorField

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

class Document(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    vector = VectorField(dimensions=512)  # Example dimensions for pgvector
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

