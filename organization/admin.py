from django.contrib import admin
from .models import Organization, Project, Repository, Document

admin.site.register(Organization)
admin.site.register(Project)
admin.site.register(Repository)
admin.site.register(Document)

