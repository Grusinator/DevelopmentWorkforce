# urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('set_pat_token/', views.set_pat_token, name='set_pat_token'),
    path('sync/', views.sync_with_ado, name='sync_with_ado'),
    path('repositories/', views.display_repositories, name='display_repositories'),
    path('repository/<int:connection_id>/update/', views.update_repository_connection,
         name='update_repository_connection'),
    path('agent/status/', views.agent_status, name='agent_status'),
]
