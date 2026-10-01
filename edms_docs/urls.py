from django.urls import path
from . import views

app_name = 'edms_docs'

urlpatterns = [
    path('', views.document_vault, name='vault'),
    path('create/modal/', views.create_document_modal, name='create_modal'),
    path('<int:pk>/revision/modal/', views.upload_revision_modal, name='upload_revision'),
    path('<int:pk>/history/modal/', views.revision_history_modal, name='revision_history'),
    path('revisions/<int:pk>/approve/', views.approve_revision, name='approve_revision'),
]
