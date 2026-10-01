from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.contact_list, name='list'),
    path('create/modal/', views.create_contact_modal, name='create_modal'),
    path('validate-document/', views.validate_document, name='validate_document'),
]
