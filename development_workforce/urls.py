from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from ninja import NinjaAPI

from development_workforce import settings
from accounts.api import router as accounts_router

api = NinjaAPI()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),
    path('accounts/', include('accounts.urls')),
    path('development/', include('development.urls')),
    path('organization/', include('organization.urls')),
    path('api/', api.urls),
    path("api/allauth/", include("allauth.headless.urls")),
]

api.add_router('/accounts/', accounts_router)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
