from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.ContactListView.as_view(), name='list'),
    path('create/', views.ContactCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.ContactDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.ContactUpdateView.as_view(), name='edit'),
    path('<uuid:pk>/archive-toggle/', views.ContactArchiveToggleView.as_view(), name='archive_toggle'),
    path('validate-document/', views.ContactValidateDocumentView.as_view(), name='validate_document'),
    path('<uuid:parent_id>/subordinate/add/', views.SubordinateContactCreateView.as_view(), name='add_subordinate'),
    path('merge/', views.ContactMergeView.as_view(), name='merge'),
    path('export/', views.ContactExportView.as_view(), name='export'),
    path('import/', views.ContactImportView.as_view(), name='import'),
    path('import/template/', views.ContactTemplateDownloadView.as_view(), name='download_template'),
]
