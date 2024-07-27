from django.db import models

from organization.models import Repository


class Document(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    # vector = VectorField(dimensions=512)  # Example dimensions for pgvector
    vector = models.CharField(max_length=3000)  # dummy for sqlite

    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
from django.db import models

# Create your models here.
