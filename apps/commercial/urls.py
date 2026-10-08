from django.urls import path
from . import views

app_name = 'commercial'

urlpatterns = [
    # Propostas Comerciais
    path('', views.ProposalListView.as_view(), name='proposal_list'),
    path('proposals/create/', views.ProposalCreateView.as_view(), name='proposal_create'),
    path('proposals/<uuid:pk>/', views.ProposalDetailView.as_view(), name='proposal_detail'),
    path('proposals/<uuid:pk>/edit/', views.ProposalUpdateView.as_view(), name='proposal_edit'),
    path('proposals/<uuid:pk>/send/', views.ProposalSendView.as_view(), name='proposal_send'),
    path('proposals/<uuid:pk>/unlock/', views.ProposalUnlockView.as_view(), name='proposal_unlock'),
    path('proposals/<uuid:pk>/print/', views.ProposalPrintView.as_view(), name='proposal_print'),
    # Autocomplete preditivo de clientes e insumos
    path('contacts/autocomplete/', views.ContactAutocompleteView.as_view(), name='contact_autocomplete'),
    path('inputs/autocomplete/', views.TechnicalInputAutocompleteView.as_view(), name='input_autocomplete'),
    path('inputs/quick-create/', views.TechnicalInputQuickCreateView.as_view(), name='input_quick_create'),

    # Itens de Escopo e Insumos Tecnicos
    path('proposals/<uuid:pk>/scope/add/', views.ProposalAddScopeItemView.as_view(), name='add_scope_item'),
    path('proposals/<uuid:pk>/scope/<uuid:item_id>/edit/', views.ProposalEditScopeItemView.as_view(), name='edit_scope_item'),
    path('proposals/<uuid:pk>/scope/<uuid:item_id>/delete/', views.ProposalDeleteScopeItemView.as_view(), name='delete_scope_item'),
    path('proposals/<uuid:pk>/inputs/add/', views.ProposalAddInputRequirementView.as_view(), name='add_input_requirement'),
    path('proposals/<uuid:pk>/inputs/<uuid:req_id>/edit/', views.ProposalEditInputRequirementView.as_view(), name='edit_input_requirement'),
    path('proposals/<uuid:pk>/inputs/<uuid:req_id>/delete/', views.ProposalDeleteInputRequirementView.as_view(), name='delete_input_requirement'),
    path('proposals/<uuid:pk>/inputs/<uuid:req_id>/validate/', views.ProposalValidateInputView.as_view(), name='validate_input'),
    # Portal Publico de Aceite Eletronico (Cliente)
    path('public/proposal/<uuid:token>/', views.ProposalPublicPortalView.as_view(), name='public_portal'),
    path('public/proposal/<uuid:token>/action/', views.ProposalPublicActionView.as_view(), name='public_action'),

    # Contratos Formais e Mise en Service
    path('contracts/<uuid:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('contracts/<uuid:pk>/edit/', views.ContractUpdateView.as_view(), name='contract_edit'),
    path('contracts/<uuid:pk>/mise-en-service/', views.ContractMiseEnServiceTriggerView.as_view(), name='trigger_mise_en_service'),
]
