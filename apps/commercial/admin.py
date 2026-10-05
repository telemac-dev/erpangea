from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    CommercialProposal,
    ProposalScopeItem,
    ProposalInputRequirement,
    LegalContract
)

class ProposalScopeItemInline(admin.TabularInline):
    model = ProposalScopeItem
    extra = 1
    fields = ('service_type', 'nbr_references', 'description', 'subtotal_value')

class ProposalInputRequirementInline(admin.TabularInline):
    model = ProposalInputRequirement
    extra = 1
    fields = ('required_item_type', 'description', 'is_mandatory', 'status', 'uploaded_file')

@admin.register(CommercialProposal)
class CommercialProposalAdmin(admin.ModelAdmin):
    inlines = [ProposalScopeItemInline, ProposalInputRequirementInline]
    list_display = (
        'proposal_code',
        'project_name',
        'client',
        'total_value',
        'status',
        'salesperson',
        'sent_at',
        'expires_at',
        'accepted_at'
    )
    list_filter = ('status', 'validity_days', 'created_at')
    search_fields = ('proposal_code', 'project_name', 'client__name', 'acceptance_signer_name')
    readonly_fields = ('proposal_code', 'public_token', 'acceptance_hash', 'accepted_at', 'acceptance_ip', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(LegalContract)
class LegalContractAdmin(admin.ModelAdmin):
    list_display = (
        'contract_code',
        'get_project_name',
        'get_client_name',
        'contract_type',
        'status',
        'd0_trigger_date',
        'deadline_date',
        'crea_art_number'
    )
    list_filter = ('status', 'contract_type', 'created_at')
    search_fields = ('contract_code', 'proposal__project_name', 'proposal__client__name', 'crea_art_number')
    readonly_fields = ('contract_code', 'd0_trigger_date', 'deadline_date', 'created_at', 'updated_at')

    @admin.display(description=_('Empreendimento / Obra'))
    def get_project_name(self, obj):
        return obj.proposal.project_name

    @admin.display(description=_('Cliente / Contratante'))
    def get_client_name(self, obj):
        return obj.proposal.client.name
