import re
from django import forms
from .models import (
    Contato, TipoPessoaChoices, TipoContato, PessoaFisica, PessoaJuridica,
    ContatoComercial, RegimeTributarioChoices, IndicadorInscricaoEstadualChoices,
    TipoVinculoChoices, VinculoContato, Interaction
)
from .utils import validate_cpf, validate_cnpj, format_cpf, format_cnpj, format_cep
from .services import add_endereco, add_telefone, add_email, set_contact_roles, create_vinculo

class PersonTypeField(forms.ChoiceField):
    def to_python(self, value):
        val = super().to_python(value)
        if val == 'PJ':
            return TipoPessoaChoices.JURIDICA
        if val == 'PF':
            return TipoPessoaChoices.FISICA
        return val

    def valid_value(self, value):
        if value in ['PJ', 'PF', TipoPessoaChoices.JURIDICA, TipoPessoaChoices.FISICA]:
            return True
        return super().valid_value(value)


class ContactForm(forms.ModelForm):
    # Odoo Header Fields
    name = forms.CharField(label="Nome ou Razão Social", max_length=255)
    trade_name = forms.CharField(label="Nome Fantasia", max_length=255, required=False)
    person_type = PersonTypeField(
        label="Tipo de Pessoa",
        choices=[
            (TipoPessoaChoices.JURIDICA, 'Empresa (Pessoa Jurídica)'),
            (TipoPessoaChoices.FISICA, 'Individual (Pessoa Física)'),
        ],
        initial=TipoPessoaChoices.JURIDICA,
        widget=forms.RadioSelect
    )

    # Odoo Company Link (Vínculo com Empresa Relacionada quando for Pessoa Física)
    parent_company = forms.ModelChoiceField(
        queryset=Contato.objects.filter(tipo_pessoa=TipoPessoaChoices.JURIDICA, deleted_at__isnull=True),
        required=False,
        label="Empresa Relacionada / Contratante"
    )
    cargo_vinculo = forms.CharField(label="Cargo / Função na Empresa", max_length=100, required=False)
    tipo_vinculo = forms.ChoiceField(label="Tipo de Vínculo", choices=TipoVinculoChoices.choices, required=False, initial=TipoVinculoChoices.CONTATO_COMERCIAL)

    document = forms.CharField(label="CPF ou CNPJ", max_length=20, required=False)
    email = forms.EmailField(label="E-mail", required=False)
    phone = forms.CharField(label="Telefone / Fixos", max_length=30, required=False)
    whatsapp = forms.CharField(label="Celular / WhatsApp", max_length=30, required=False)
    website = forms.URLField(label="Website", required=False)
    
    zip_code = forms.CharField(label="CEP", max_length=10, required=False)
    address = forms.CharField(label="Logradouro / Número / Bairro", max_length=255, required=False)
    city = forms.CharField(label="Cidade / Município", max_length=100, required=False)
    state = forms.CharField(label="UF", max_length=2, required=False)
    
    roles = forms.ModelMultipleChoiceField(
        queryset=TipoContato.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Etiquetas / Papéis do Contato"
    )

    # Odoo Tab: Pessoa Física Fields
    rg = forms.CharField(label="RG", max_length=20, required=False)
    profissao = forms.CharField(label="Profissão", max_length=100, required=False)
    conselho_profissional = forms.CharField(label="Conselho Profissional (ex: CREA)", max_length=50, required=False)
    registro_profissional = forms.CharField(label="Registro Profissional", max_length=50, required=False)

    # Odoo Tab: Pessoa Jurídica / Fiscal Fields
    inscricao_estadual = forms.CharField(label="Inscrição Estadual", max_length=30, required=False)
    inscricao_municipal = forms.CharField(label="Inscrição Municipal", max_length=30, required=False)
    indicador_inscricao_estadual = forms.ChoiceField(label="Indicador de IE", choices=IndicadorInscricaoEstadualChoices.choices, required=False)
    regime_tributario = forms.ChoiceField(label="Regime Tributário", choices=RegimeTributarioChoices.choices, required=False)

    # Odoo Tab: Vendas & Compras / Bancário Fields
    limite_credito = forms.DecimalField(label="Limite de Crédito (R$)", max_digits=12, decimal_places=2, required=False, initial=0.00)
    condicao_pagamento = forms.CharField(label="Condição Padrão de Pagamento", max_length=100, required=False)
    banco = forms.CharField(label="Banco", max_length=50, required=False)
    agencia = forms.CharField(label="Agência", max_length=20, required=False)
    conta = forms.CharField(label="Conta Bancária", max_length=30, required=False)
    pix = forms.CharField(label="Chave Pix", max_length=255, required=False)

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

            if self.instance.tipo_pessoa == TipoPessoaChoices.FISICA:
                v = self.instance.vinculos_como_pf.filter(ativo=True).first()
                if v:
                    self.fields['parent_company'].initial = v.pessoa_juridica
                    self.fields['cargo_vinculo'].initial = v.cargo
                    self.fields['tipo_vinculo'].initial = v.tipo_vinculo

            if hasattr(self.instance, 'pessoa_fisica') and self.instance.pessoa_fisica:
                pf = self.instance.pessoa_fisica
                self.fields['rg'].initial = pf.rg
                self.fields['profissao'].initial = pf.profissao
                self.fields['conselho_profissional'].initial = pf.conselho_profissional
                self.fields['registro_profissional'].initial = pf.registro_profissional
                self.fields['whatsapp'].initial = pf.whatsapp

            if hasattr(self.instance, 'pessoa_juridica') and self.instance.pessoa_juridica:
                pj = self.instance.pessoa_juridica
                self.fields['inscricao_estadual'].initial = pj.inscricao_estadual
                self.fields['inscricao_municipal'].initial = pj.inscricao_municipal
                self.fields['indicador_inscricao_estadual'].initial = pj.indicador_inscricao_estadual
                self.fields['regime_tributario'].initial = pj.regime_tributario
                self.fields['website'].initial = pj.site

            if hasattr(self.instance, 'dados_comerciais') and self.instance.dados_comerciais:
                com = self.instance.dados_comerciais
                self.fields['limite_credito'].initial = com.limite_credito
                self.fields['condicao_pagamento'].initial = com.condicao_pagamento
                self.fields['banco'].initial = com.banco
                self.fields['agencia'].initial = com.agencia
                self.fields['conta'].initial = com.conta
                self.fields['pix'].initial = com.pix

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
            
            roles = self.cleaned_data.get('roles')
            if roles:
                role_codes = [r.codigo for r in roles]
                set_contact_roles(contato, role_codes)

            doc = self.cleaned_data.get('document')
            email = self.cleaned_data.get('email')
            phone = self.cleaned_data.get('phone')
            whatsapp = self.cleaned_data.get('whatsapp')
            website = self.cleaned_data.get('website')
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
                if whatsapp:
                    pf.whatsapp = whatsapp
                pf.rg = self.cleaned_data.get('rg', '')
                pf.profissao = self.cleaned_data.get('profissao', '')
                pf.conselho_profissional = self.cleaned_data.get('conselho_profissional', '')
                pf.registro_profissional = self.cleaned_data.get('registro_profissional', '')
                pf.save()

                # Handle Parent Company Link (Vínculo com PJ)
                parent_comp = self.cleaned_data.get('parent_company')
                if parent_comp:
                    cargo = self.cleaned_data.get('cargo_vinculo', '')
                    t_vinc = self.cleaned_data.get('tipo_vinculo', TipoVinculoChoices.CONTATO_COMERCIAL)
                    create_vinculo(pf_contato=contato, pj_contato=parent_comp, cargo=cargo, tipo_vinculo=t_vinc)
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
                if website:
                    pj.site = website
                pj.inscricao_estadual = self.cleaned_data.get('inscricao_estadual', '')
                pj.inscricao_municipal = self.cleaned_data.get('inscricao_municipal', '')
                pj.indicador_inscricao_estadual = self.cleaned_data.get('indicador_inscricao_estadual', IndicadorInscricaoEstadualChoices.NAO_INFORMADO)
                pj.regime_tributario = self.cleaned_data.get('regime_tributario', RegimeTributarioChoices.NAO_INFORMADO)
                pj.save()

            # Save Commercial / Bank data
            com, _ = ContatoComercial.objects.get_or_create(contato=contato)
            if self.cleaned_data.get('limite_credito') is not None:
                com.limite_credito = self.cleaned_data.get('limite_credito')
            com.condicao_pagamento = self.cleaned_data.get('condicao_pagamento', '')
            com.banco = self.cleaned_data.get('banco', '')
            com.agencia = self.cleaned_data.get('agencia', '')
            com.conta = self.cleaned_data.get('conta', '')
            com.pix = self.cleaned_data.get('pix', '')
            com.save()

            if email:
                add_email(contato, email=email, principal=True)
            if phone:
                add_telefone(contato, numero=phone, principal=True)
            if whatsapp and whatsapp != phone:
                add_telefone(contato, numero=whatsapp, tipo='WHATSAPP', whatsapp=True)
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
