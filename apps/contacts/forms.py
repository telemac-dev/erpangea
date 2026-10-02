from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Contact, ContactTag, ContactTypeChoices, AddressTypeChoices, DocTypeChoices
from .validators import clean_doc_digits, format_document

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'contact_type', 'name', 'trade_name', 'parent',
            'doc_type', 'doc_number', 'state_registration', 'municipal_registration', 'suframa_code',
            'street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code', 'country',
            'phone', 'mobile', 'email', 'website', 'job_title',
            'salesperson', 'payment_terms', 'tags',
            'avatar', 'internal_notes'
        ]
        widgets = {
            'contact_type': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'ex.: Pangea Engenharia Ltda. ou Dr. Carlos Silva', 'autofocus': True}),
            'trade_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Fantasia corporativo'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'doc_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_doc_type'}),
            'doc_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas números ou formatado', 'id': 'id_doc_number'}),
            'state_registration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inscrição Estadual'}),
            'municipal_registration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inscrição Municipal'}),
            'suframa_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código SUFRAMA'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Logradouro / Rua / Avenida'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nº'}),
            'complement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complemento / Bloco'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF (ex: SP)', 'maxlength': '2'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000', 'id': 'id_postal_code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 3333-4444'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 9 9999-8888'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contato@empresa.com.br'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.empresa.com.br'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex.: Diretor de Operações / Engenheiro'}),
            'salesperson': forms.Select(attrs={'class': 'form-select'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex.: 30 dias / À vista'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '4'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Observações confidenciais e histórico interno...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra empresas elegiveis para relacionamento pai
        company_qs = Contact.objects.filter(contact_type=ContactTypeChoices.COMPANY, is_active=True)
        if self.instance and self.instance.pk:
            company_qs = company_qs.exclude(pk=self.instance.pk)
        self.fields['parent'].queryset = company_qs
        self.fields['parent'].empty_label = _("(Nenhuma empresa vinculada - Contato Independente)")

        # País default Brasil
        self.fields['country'].required = False
        if not self.instance.country:
            self.fields['country'].initial = 'Brasil'

        # Formata doc_number inicial
        if self.instance and self.instance.doc_number:
            self.fields['doc_number'].initial = self.instance.formatted_doc_number

class SubordinateContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'address_type', 'name', 'job_title', 'email', 'phone', 'mobile',
            'street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code',
            'internal_notes'
        ]
        widgets = {
            'address_type': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Contato ou Identificador do Endereço'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo / Função'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@empresa.com.br'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone direto'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Logradouro'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'complement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complemento'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF', 'maxlength': '2'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CEP'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observações adicionais...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address_type'].initial = AddressTypeChoices.CONTACT

class ContactTagForm(forms.ModelForm):
    class Meta:
        model = ContactTag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Marcador (ex: VIP, Fornecedor Solo)'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
        }

class ContactMergeForm(forms.Form):
    destination_contact = forms.ModelChoiceField(
        queryset=Contact.objects.none(),
        label=_("Contato de Destino Definitivo"),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        contacts = kwargs.pop('contacts', Contact.objects.none())
        super().__init__(*args, **kwargs)
        self.fields['destination_contact'].queryset = contacts

class ContactUploadImportForm(forms.Form):
    file = forms.FileField(
        label=_("Arquivo de Dados (.xlsx ou .csv)"),
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.csv'})
    )
