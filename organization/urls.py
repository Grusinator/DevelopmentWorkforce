# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('input_pat_token/', views.input_pat_token, name='input_pat_token'),
    path('agent_work_permits/', views.agent_work_permits, name='agent_work_permits'),
    path('list_work_permits/', views.list_work_permits, name='list_work_permits'),
    path('fetch_projects_and_repos/', views.fetch_projects_and_repos, name='fetch_projects_and_repos'),
]