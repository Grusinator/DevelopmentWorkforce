# urls.py
from django.urls import path

from .views.agent_view import agent_status
from .views.views import set_pat_token, sync_with_ado, display_repositories, update_repository_connection

urlpatterns = [
    path('set_pat_token/', set_pat_token, name='set_pat_token'),
    path('sync/', sync_with_ado, name='sync_with_ado'),
    path('repositories/', display_repositories, name='display_repositories'),
    path('repository/<int:connection_id>/update/', update_repository_connection,
         name='update_repository_connection'),
    path('agent/status/', agent_status, name='agent_status'),
]
