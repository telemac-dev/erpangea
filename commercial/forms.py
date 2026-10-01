from django import forms
from .models import Proposal, Contract, WorkOrder

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['cliente', 'disciplina_principal', 'valor_global', 'validade']
        widgets = {
            'validade': forms.DateInput(attrs={'type': 'date'}),
        }

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['data_assinatura', 'data_vigencia_inicio', 'data_vigencia_fim', 'modalidade_cobranca', 'documento_assinado']
        widgets = {
            'data_assinatura': forms.DateInput(attrs={'type': 'date'}),
            'data_vigencia_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_vigencia_fim': forms.DateInput(attrs={'type': 'date'}),
        }

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['coordenador_tecnico', 'status']
