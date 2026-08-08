from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_list, name='contact_list'),
    path('novo/', views.contact_create, name='contact_create'),
    path('<uuid:pk>/', views.contact_detail, name='contact_detail'),
    path('<uuid:pk>/editar/', views.contact_edit, name='contact_edit'),
    path('<uuid:pk>/excluir/', views.contact_delete, name='contact_delete'),
    path('format-document-hx/', views.format_document_hx, name='format_document_hx'),
    path('lookup-cep-hx/', views.lookup_cep_hx, name='lookup_cep_hx'),
    path('related-company-hx/', views.related_company_hx, name='related_company_hx'),
    path('add-vinculo-modal-hx/', views.add_vinculo_modal_hx, name='add_vinculo_modal_hx'),
]
