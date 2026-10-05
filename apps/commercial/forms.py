from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    CommercialProposal,
    ProposalScopeItem,
    ProposalInputRequirement,
    LegalContract,
    ServiceTypeChoices,
    InputItemTypeChoices,
    InputStatusChoices,
    ContractTypeChoices
)
from apps.contacts.models import Contact

class ProposalForm(forms.ModelForm):
    class Meta:
        model = CommercialProposal
        fields = [
            'client', 'project_name', 'project_location',
            'salesperson', 'technical_responsible',
            'validity_days', 'execution_lead_time_days',
            'total_value', 'payment_terms_desc'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select', 'id': 'id_client'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex.: Edifício Residencial Parque das Laranjeiras'}),
            'project_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex.: Av. Coronel Teixeira, Ponta Negra, Manaus/AM'}),
            'salesperson': forms.Select(attrs={'class': 'form-select'}),
            'technical_responsible': forms.Select(attrs={'class': 'form-select'}),
            'validity_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 90}),
            'execution_lead_time_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 365}),
            'total_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_total_value'}),
            'payment_terms_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'ex.: 50% de entrada no aceite e 50% na entrega final do projeto executivo.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Contact.objects.filter(is_active=True).order_by('name')

class ProposalScopeItemForm(forms.ModelForm):
    class Meta:
        model = ProposalScopeItem
        fields = ['service_type', 'nbr_references', 'description', 'subtotal_value']
        widgets = {
            'service_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_service_type'}),
            'nbr_references': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex.: ABNT NBR 6122:2019 e NBR 6118:2023'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Memorial descritivo detalhado do escopo a ser entregue...'}),
            'subtotal_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }

class ProposalInputRequirementForm(forms.ModelForm):
    class Meta:
        model = ProposalInputRequirement
        fields = ['required_item_type', 'description', 'is_mandatory']
        widgets = {
            'required_item_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especificação técnica mínima necessária'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TechnicalInputValidationForm(forms.ModelForm):
    """
    Formulário para o engenheiro geotécnico anexar arquivos ou emitir parecer de aprovação/rejeição.
    """
    class Meta:
        model = ProposalInputRequirement
        fields = ['status', 'uploaded_file', 'technical_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'uploaded_file': forms.FileInput(attrs={'class': 'form-control'}),
            'technical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Parecer técnico sobre conformidade com normas ABNT...'}),
        }

class LegalContractForm(forms.ModelForm):
    class Meta:
        model = LegalContract
        fields = [
            'contract_type', 'contract_html_body',
            'signed_pdf', 'signed_at',
            'crea_art_number', 'crea_art_file'
        ]
        widgets = {
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'contract_html_body': forms.Textarea(attrs={'class': 'form-control', 'rows': 12, 'style': 'font-family: monospace; font-size: 0.85rem;'}),
            'signed_pdf': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'signed_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'crea_art_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número do Registro da ART no CREA-AM'}),
            'crea_art_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

class OnlineAcceptanceForm(forms.Form):
    signer_name = forms.CharField(
        label=_("Nome Completo do Representante Legal"),
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex.: Dr. Antônio Carlos Fagundes', 'required': True})
    )
    signer_doc = forms.CharField(
        label=_("CPF ou CNPJ do Signatário"),
        max_length=25,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00 ou 00.000.000/0000-00', 'required': True})
    )
    signer_role = forms.CharField(
        label=_("Cargo / Poderes de Representação"),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex.: Diretor Presidente / Procurador', 'required': True})
    )
    confirm_terms = forms.BooleanField(
        label=_("Declaro que li e concordo integralmente com os termos técnicos, escopo, valores e condições suspensivas expressas nesta proposta."),
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class ClientRevisionRequestForm(forms.Form):
    revision_notes = forms.CharField(
        label=_("Observações e Solicitação de Revisão de Escopo / Condições"),
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva detalhadamente as alterações solicitadas para análise técnica da Pangea Engenharia...'})
    )

class ClientRejectionForm(forms.Form):
    rejection_reason = forms.CharField(
        label=_("Motivo da Recusa da Proposta Comercial"),
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Por favor, informe o motivo do declínio (ex: orçamento cancelado, prazo incompatível, etc.)...'})
    )
