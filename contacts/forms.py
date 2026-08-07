import re
from django import forms
from .models import Contato, TipoPessoaChoices, TipoContato, PessoaFisica, PessoaJuridica, Interaction
from .utils import validate_cpf, validate_cnpj, format_cpf, format_cnpj, format_cep
from .services import add_endereco, add_telefone, add_email, set_contact_roles

class ContactForm(forms.ModelForm):
    # Form fields for clean representation
    name = forms.CharField(label="Nome ou Razão Social", max_length=255)
    trade_name = forms.CharField(label="Nome Fantasia", max_length=255, required=False)
    person_type = forms.ChoiceField(
        label="Tipo de Pessoa",
        choices=[
            (TipoPessoaChoices.JURIDICA, 'Pessoa Jurídica'),
            (TipoPessoaChoices.FISICA, 'Pessoa Física'),
            ('PJ', 'Pessoa Jurídica'),
            ('PF', 'Pessoa Física'),
        ],
        initial=TipoPessoaChoices.JURIDICA
    )
    document = forms.CharField(label="CPF ou CNPJ", max_length=20, required=False)
    email = forms.EmailField(label="E-mail", required=False)
    phone = forms.CharField(label="Telefone / WhatsApp", max_length=30, required=False)
    zip_code = forms.CharField(label="CEP", max_length=10, required=False)
    address = forms.CharField(label="Logradouro / Número / Bairro", max_length=255, required=False)
    city = forms.CharField(label="Cidade / Município", max_length=100, required=False)
    state = forms.CharField(label="UF", max_length=2, required=False)
    
    roles = forms.ModelMultipleChoiceField(
        queryset=TipoContato.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Funções no Sistema"
    )

    class Meta:
        model = Contato
        fields = ['ativo', 'observacoes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['name'].initial = self.instance.nome_razao_social
            self.fields['trade_name'].initial = self.instance.nome_fantasia
            self.fields['person_type'].initial = self.instance.tipo_pessoa
            self.fields['document'].initial = self.instance.document
            self.fields['email'].initial = self.instance.email
            self.fields['phone'].initial = self.instance.phone
            self.fields['zip_code'].initial = self.instance.zip_code
            self.fields['address'].initial = self.instance.address
            self.fields['city'].initial = self.instance.city
            self.fields['state'].initial = self.instance.state
            self.fields['roles'].initial = self.instance.roles

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

            if person_type == TipoPessoaChoices.FISICA or person_type == 'PF':
                if not validate_cpf(digits):
                    self.add_error(
                        'document',
                        'CPF inválido. Informe um número de CPF válido com 11 dígitos (ex: 123.456.789-00).'
                    )
                else:
                    cleaned_data['document'] = format_cpf(digits)

            elif person_type == TipoPessoaChoices.JURIDICA or person_type == 'PJ':
                if not validate_cnpj(digits):
                    self.add_error(
                        'document',
                        'CNPJ inválido. Informe um número de CNPJ válido com 14 dígitos (ex: 12.345.678/0001-12).'
                    )
                else:
                    cleaned_data['document'] = format_cnpj(digits)

        return cleaned_data

    def save(self, commit=True):
        contato = super().save(commit=False)
        contato.nome_razao_social = self.cleaned_data['name']
        contato.nome_fantasia = self.cleaned_data.get('trade_name', '')
        pt = self.cleaned_data['person_type']
        contato.tipo_pessoa = TipoPessoaChoices.FISICA if pt in ['PF', TipoPessoaChoices.FISICA] else TipoPessoaChoices.JURIDICA
        
        if commit:
            contato.save()
            
            # Save roles
            roles = self.cleaned_data.get('roles')
            if roles:
                role_codes = [r.codigo for r in roles]
                set_contact_roles(contato, role_codes)

            doc = self.cleaned_data.get('document')
            email = self.cleaned_data.get('email')
            phone = self.cleaned_data.get('phone')
            logradouro = self.cleaned_data.get('address')
            city = self.cleaned_data.get('city')
            state = self.cleaned_data.get('state')
            cep = self.cleaned_data.get('zip_code')

            # Create or update PF / PJ sub-model
            if contato.tipo_pessoa == TipoPessoaChoices.FISICA:
                pf, _ = PessoaFisica.objects.get_or_create(contato=contato)
                if doc:
                    pf.cpf = doc
                if email:
                    pf.email_pessoal = email
                if phone:
                    pf.telefone_pessoal = phone
                pf.save()
            else:
                pj, _ = PessoaJuridica.objects.get_or_create(contato=contato)
                pj.razao_social = contato.nome_razao_social
                pj.nome_fantasia = contato.nome_fantasia
                if doc:
                    pj.cnpj = doc
                if email:
                    pj.email_comercial = email
                if phone:
                    pj.telefone_comercial = phone
                if city:
                    pj.municipio = city
                if state:
                    pj.uf = state
                pj.save()

            if email:
                add_email(contato, email=email, principal=True)
            if phone:
                add_telefone(contato, numero=phone, principal=True)
            if logradouro or city or state or cep:
                add_endereco(contato, logradouro=logradouro or 'Endereço Principal', municipio=city or '', uf=state or '', cep=cep or '', principal=True)

        return contato


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
