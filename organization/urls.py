# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('set_pat_token/', views.set_pat_token, name='set_pat_token'),
    path('agent_work_permits/', views.agent_work_permits, name='agent_work_permits'),
    path('list_work_permits/', views.list_work_permits, name='work_permits'),
    path('sync/', views.sync_with_ado, name='sync_with_ado'),
    path('projects/', views.display_projects, name='projects'),
]
