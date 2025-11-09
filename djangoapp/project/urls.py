from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', views.dashboard, name='dashboard'),
    # Rota temporária para capturar todas as URLs /temp/
    path('temp/', include('accounts.urls')),
    # ... outras URLs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    #urlpatterns += static(
    #    settings.STATIC_URL, 
    #    document_root=settings.STATIC_ROOT)
    