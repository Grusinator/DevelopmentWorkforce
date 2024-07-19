from django.urls import include
from django.urls import path

from accounts.views import manage_profile

urlpatterns = [
    path('', include('allauth.urls')),
    path('profile/', manage_profile, name='manage_profile'),
]
