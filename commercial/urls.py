from django.urls import path
from . import views

urlpatterns = [
    # Leads
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/novo/', views.lead_create, name='lead_create'),
    path('leads/<int:pk>/editar/', views.lead_edit, name='lead_edit'),
    
    # Proposals
    path('propostas/', views.proposal_list, name='proposal_list'),
    path('propostas/nova/', views.proposal_create, name='proposal_create'),
    path('propostas/<int:pk>/', views.proposal_detail, name='proposal_detail'),
    path('propostas/<int:pk>/editar/', views.proposal_edit, name='proposal_edit'),
    path('propostas/<int:pk>/nova-versao/', views.proposal_create_new_version, name='proposal_create_new_version'),
    
    # Contracts
    path('contratos/', views.contract_list, name='contract_list'),
    path('contratos/novo/', views.contract_create, name='contract_create'),
]
