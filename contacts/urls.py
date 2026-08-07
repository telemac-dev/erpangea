from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_list, name='contact_list'),
    path('novo/', views.contact_create, name='contact_create'),
    path('<int:pk>/', views.contact_detail, name='contact_detail'),
    path('<int:pk>/editar/', views.contact_edit, name='contact_edit'),
    path('<int:pk>/excluir/', views.contact_delete, name='contact_delete'),
    path('format-document-hx/', views.format_document_hx, name='format_document_hx'),
    path('lookup-cep-hx/', views.lookup_cep_hx, name='lookup_cep_hx'),
]
