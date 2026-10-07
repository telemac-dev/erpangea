from decimal import Decimal
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
    ContractTypeChoices,
    TechnicalDiscipline,
    TechnicalServiceType,
    TechnicalInputType
)
from apps.contacts.models import Contact
from .templatetags.currency_filters import parse_decimal_br, number_br

class ProposalForm(forms.ModelForm):
    total_value = forms.CharField(
        label=_('Valor Estimado da Proposta (R$)'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-end font-monospace',
            'id': 'id_total_value',
            'placeholder': '0,00'
        })
    )

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
            'payment_terms_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'ex.: 50% de entrada no aceite e 50% na entrega final do projeto executivo.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Contact.objects.filter(is_active=True).order_by('name')
        if self.instance and self.instance.pk:
            self.fields['total_value'].initial = number_br(self.instance.total_value)

    def clean_total_value(self):
        raw = self.cleaned_data.get('total_value')
        return parse_decimal_br(raw)


class ProposalScopeItemForm(forms.ModelForm):
    discipline_name = forms.CharField(
        label=_('Disciplina Técnica'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'datalist_disciplines',
            'placeholder': 'Selecione ou digite uma nova disciplina...',
            'id': 'id_discipline_name'
        })
    )
    service_type_name = forms.CharField(
        label=_('Tipo de Serviço / Escopo'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'datalist_service_types',
            'placeholder': 'Selecione ou digite um novo tipo de serviço...',
            'id': 'id_service_type_name'
        })
    )
    subtotal_value = forms.CharField(
        label=_('Subtotal Precificado (R$)'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-end font-monospace',
            'placeholder': '0,00',
            'id': 'id_subtotal_value'
        })
    )

    class Meta:
        model = ProposalScopeItem
        fields = ['nbr_references', 'description']
        widgets = {
            'nbr_references': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_nbr_references',
                'placeholder': 'ex.: ABNT NBR 6122:2019 e NBR 6118:2023'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'id_description',
                'rows': 3,
                'placeholder': 'Memorial descritivo detalhado do escopo a ser entregue...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and not self.instance._state.adding:
            self.fields['service_type_name'].initial = self.instance.get_service_type_display()
            if self.instance.discipline:
                self.fields['discipline_name'].initial = self.instance.discipline.name
            elif self.instance.service_type_ref and self.instance.service_type_ref.discipline:
                self.fields['discipline_name'].initial = self.instance.service_type_ref.discipline.name
            self.fields['subtotal_value'].initial = number_br(self.instance.subtotal_value)
        else:
            # No modo de adição: todos os campos iniciam estritamente vazios, exibindo apenas o placeholder
            self.initial['service_type_name'] = ''
            self.initial['discipline_name'] = ''
            self.initial['nbr_references'] = ''
            self.initial['description'] = ''
            self.initial['subtotal_value'] = ''
            self.fields['service_type_name'].initial = ''
            self.fields['discipline_name'].initial = ''
            self.fields['nbr_references'].initial = ''
            self.fields['description'].initial = ''
            self.fields['subtotal_value'].initial = ''
    def clean_subtotal_value(self):
        raw = self.cleaned_data.get('subtotal_value')
        dec = parse_decimal_br(raw)
        if dec < Decimal('0.00'):
            raise forms.ValidationError(_("O valor do subtotal não pode ser negativo."))
        return dec

    def save(self, commit=True):
        item = super().save(commit=False)
        disc_name = self.cleaned_data.get('discipline_name', '').strip()
        disc_obj = None
        if disc_name:
            disc_obj, _ = TechnicalDiscipline.objects.get_or_create(
                name=disc_name,
                defaults={'is_active': True}
            )

        serv_name = self.cleaned_data.get('service_type_name', '').strip()
        if not serv_name and self.data.get('service_type'):
            legacy_choice = self.data.get('service_type')
            serv_name = dict(ServiceTypeChoices.choices).get(legacy_choice, legacy_choice)

        if serv_name:
            serv_obj, _ = TechnicalServiceType.objects.get_or_create(
                name=serv_name,
                defaults={
                    'discipline': disc_obj,
                    'default_nbr_references': self.cleaned_data.get('nbr_references', ''),
                    'default_description': self.cleaned_data.get('description', ''),
                    'is_active': True
                }
            )
            if disc_obj and not serv_obj.discipline:
                serv_obj.discipline = disc_obj
                serv_obj.save()

            item.service_type_ref = serv_obj
            item.service_type = serv_obj.name
            item.discipline = disc_obj or (serv_obj.discipline if serv_obj else None)

        item.subtotal_value = self.cleaned_data.get('subtotal_value')

        if commit:
            item.save()
        return item


class ProposalInputRequirementForm(forms.ModelForm):
    input_type_name = forms.CharField(
        label=_('Tipo do Insumo Obrigatório'),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'datalist_input_types',
            'placeholder': 'Selecione ou digite um novo tipo de insumo...',
            'id': 'id_input_type_name'
        })
    )

    class Meta:
        model = ProposalInputRequirement
        fields = ['description', 'is_mandatory']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_input_description',
                'placeholder': 'Especificação técnica mínima necessária'
            }),
            'is_mandatory': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_mandatory'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and not self.instance._state.adding:
            self.fields['input_type_name'].initial = self.instance.get_required_item_type_display()
        else:
            self.initial['input_type_name'] = ''
            self.initial['description'] = ''
            self.fields['input_type_name'].initial = ''
            self.fields['description'].initial = ''
    def save(self, commit=True):
        req_item = super().save(commit=False)
        input_name = self.cleaned_data.get('input_type_name', '').strip()
        if not input_name and self.data.get('required_item_type'):
            legacy_choice = self.data.get('required_item_type')
            input_name = dict(InputItemTypeChoices.choices).get(legacy_choice, legacy_choice)

        if input_name:
            inp_obj, _ = TechnicalInputType.objects.get_or_create(
                name=input_name,
                defaults={
                    'default_description': self.cleaned_data.get('description', ''),
                    'is_mandatory_default': self.cleaned_data.get('is_mandatory', True),
                    'is_active': True
                }
            )
            req_item.input_type_ref = inp_obj
            req_item.required_item_type = inp_obj.name

        if commit:
            req_item.save()
        return req_item
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
