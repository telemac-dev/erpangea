from django import forms
from .models import Lead, Proposal, Contract

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'contact', 'source', 'service_of_interest', 'description',
            'estimated_value', 'probability', 'assigned_to', 'stage',
            'expected_closing_date', 'notes'
        ]
        widgets = {
            'expected_closing_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = [
            'number', 'client', 'lead', 'scope', 'included_services',
            'exclusions', 'assumptions', 'execution_period_days',
            'validity_days', 'total_value', 'payment_terms',
            'technical_responsible', 'commercial_responsible', 'status'
        ]

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'number', 'client', 'proposal', 'start_date', 'end_date',
            'total_value', 'payment_terms', 'readjustment_index',
            'status', 'responsible', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
