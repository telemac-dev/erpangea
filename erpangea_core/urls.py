from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', login_required(TemplateView.as_view(template_name='dashboard.html')), name='dashboard'),
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('contacts/', include('contacts.urls')),
    path('commercial/', include('commercial.urls')),
    path('projects/', include('projects.urls')),
    path('edms/', include('edms_docs.urls')),
    path('measurements/', include('measurements.urls')),
    path('invoices/', include('invoices.urls')),
    path('financial/', include('financial.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
