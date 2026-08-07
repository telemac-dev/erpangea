import re
from django import forms
from .models import Contact, Interaction, ContactRole, PersonTypeChoices
from .utils import validate_cpf, validate_cnpj, format_cpf, format_cnpj, format_cep

class ContactForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=ContactRole.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Funções no Sistema"
    )

    class Meta:
        model = Contact
        fields = [
            'name', 'trade_name', 'person_type', 'document',
            'email', 'phone', 'zip_code', 'address', 'city', 'state',
            'website', 'notes', 'is_active', 'roles'
        ]

    def clean(self):
        cleaned_data = super().clean()
        person_type = cleaned_data.get('person_type')
        document_raw = cleaned_data.get('document', '')
        zip_code_raw = cleaned_data.get('zip_code', '')

        if zip_code_raw:
            zip_digits = re.sub(r'\D', '', str(zip_code_raw))
            if zip_digits:
                cleaned_data['zip_code'] = format_cep(zip_digits)

        if document_raw:
            digits = re.sub(r'\D', '', str(document_raw))

            if person_type == PersonTypeChoices.PF:
                if not validate_cpf(digits):
                    self.add_error(
                        'document',
                        'CPF inválido. Informe um número de CPF válido com 11 dígitos (ex: 123.456.789-00).'
                    )
                else:
                    cleaned_data['document'] = format_cpf(digits)

            elif person_type == PersonTypeChoices.PJ:
                if not validate_cnpj(digits):
                    self.add_error(
                        'document',
                        'CNPJ inválido. Informe um número de CNPJ válido com 14 dígitos (ex: 12.345.678/0001-12).'
                    )
                else:
                    cleaned_data['document'] = format_cnpj(digits)

        return cleaned_data

class InteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = [
            'interaction_type', 'subject', 'description',
            'next_action', 'next_action_deadline'
        ]
        widgets = {
            'next_action_deadline': forms.DateInput(attrs={'type': 'date'}),
        }
