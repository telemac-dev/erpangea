from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import health_check, dashboard_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('health/', health_check, name='health_check'),
    path('accounts/', include('apps.accounts.urls')),
    path('contacts/', include('apps.contacts.urls')),
    path('commercial/', include('apps.commercial.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
