import uuid
import re
from django.db import models
from django.conf import settings
from django.utils import timezone
from .validators import validate_cpf_digits, validate_cnpj_digits, validate_cep_digits

class TipoPessoaChoices(models.TextChoices):
    FISICA = 'FISICA', 'Pessoa Física'
    JURIDICA = 'JURIDICA', 'Pessoa Jurídica'

# Reverse choices for legacy compatibility
PersonTypeChoices = TipoPessoaChoices

class CodigoTipoContatoChoices(models.TextChoices):
    CLIENTE = 'CLIENTE', 'Cliente'
    PROFISSIONAL = 'PROFISSIONAL', 'Profissional'
    ORGAO_PUBLICO = 'ORGAO_PUBLICO', 'Órgão Público'
    PARCEIRO = 'PARCEIRO', 'Parceiro'
    FORNECEDOR = 'FORNECEDOR', 'Fornecedor'
    EMPREENDIMENTO = 'EMPREENDIMENTO', 'Empreendimento'
    PRESTADOR_SERVICO = 'PRESTADOR_SERVICO', 'Prestador de Serviço'
    TOMADOR_SERVICO = 'TOMADOR_SERVICO', 'Tomador de Serviço'

# Legacy choices mapping
ContactRoleChoices = CodigoTipoContatoChoices


class TipoContato(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField('Código', max_length=50, choices=CodigoTipoContatoChoices.choices, unique=True)
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)

    class Meta:
        verbose_name = 'Tipo de Contato'
        verbose_name_plural = 'Tipos de Contato'

    def __str__(self):
        return self.get_codigo_display() or self.nome

# Legacy alias
ContactRole = TipoContato


class Contato(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_pessoa = models.CharField('Tipo de Pessoa', max_length=10, choices=TipoPessoaChoices.choices, default=TipoPessoaChoices.JURIDICA)
    nome_razao_social = models.CharField('Nome / Razão Social', max_length=255)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=255, blank=True)
    nome_social = models.CharField('Nome Social', max_length=255, blank=True)
    apelido = models.CharField('Apelido', max_length=255, blank=True)
    
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contatos', verbose_name='Criado por')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_contatos', verbose_name='Atualizado por')
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    deleted_at = models.DateTimeField('Excluído em (Soft Delete)', null=True, blank=True)

    class Meta:
        ordering = ['nome_razao_social']
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        indexes = [
            models.Index(fields=['nome_razao_social']),
            models.Index(fields=['tipo_pessoa']),
            models.Index(fields=['ativo']),
            models.Index(fields=['deleted_at']),
        ]

    # --- Backward compatibility properties for existing modules ---
    @property
    def name(self):
        return self.nome_razao_social
    
    @name.setter
    def name(self, val):
        self.nome_razao_social = val

    @property
    def trade_name(self):
        return self.nome_fantasia

    @trade_name.setter
    def trade_name(self, val):
        self.nome_fantasia = val

    @property
    def person_type(self):
        return 'PF' if self.tipo_pessoa == TipoPessoaChoices.FISICA else 'PJ'

    @person_type.setter
    def person_type(self, val):
        self.tipo_pessoa = TipoPessoaChoices.FISICA if val == 'PF' else TipoPessoaChoices.JURIDICA

    @property
    def is_active(self):
        return self.ativo and self.deleted_at is None

    @is_active.setter
    def is_active(self, val):
        self.ativo = val

    @property
    def document(self):
        if hasattr(self, 'pessoa_fisica') and self.pessoa_fisica and self.pessoa_fisica.cpf:
            return self.pessoa_fisica.formatted_cpf
        if hasattr(self, 'pessoa_juridica') and self.pessoa_juridica and self.pessoa_juridica.cnpj:
            return self.pessoa_juridica.formatted_cnpj
        return ""

    @property
    def email(self):
        email_obj = self.emails.filter(principal=True).first() or self.emails.first()
        if email_obj:
            return email_obj.email
        if hasattr(self, 'pessoa_juridica') and self.pessoa_juridica.email_comercial:
            return self.pessoa_juridica.email_comercial
        if hasattr(self, 'pessoa_fisica') and self.pessoa_fisica.email_pessoal:
            return self.pessoa_fisica.email_pessoal
        return ""

    @property
    def phone(self):
        phone_obj = self.telefones.filter(principal=True).first() or self.telefones.first()
        if phone_obj:
            return phone_obj.numero
        if hasattr(self, 'pessoa_juridica') and self.pessoa_juridica.telefone_comercial:
            return self.pessoa_juridica.telefone_comercial
        if hasattr(self, 'pessoa_fisica') and self.pessoa_fisica.telefone_pessoal:
            return self.pessoa_fisica.telefone_pessoal
        return ""

    @property
    def address(self):
        end_obj = self.enderecos.filter(principal=True).first() or self.enderecos.first()
        if end_obj:
            return end_obj.endereco.format_address
        return ""

    @property
    def city(self):
        end_obj = self.enderecos.filter(principal=True).first() or self.enderecos.first()
        if end_obj:
            return end_obj.endereco.municipio
        if hasattr(self, 'pessoa_juridica') and self.pessoa_juridica.municipio:
            return self.pessoa_juridica.municipio
        return ""

    @property
    def state(self):
        end_obj = self.enderecos.filter(principal=True).first() or self.enderecos.first()
        if end_obj:
            return end_obj.endereco.uf
        if hasattr(self, 'pessoa_juridica') and self.pessoa_juridica.uf:
            return self.pessoa_juridica.uf
        return ""

    @property
    def zip_code(self):
        end_obj = self.enderecos.filter(principal=True).first() or self.enderecos.first()
        if end_obj:
            return end_obj.endereco.formatted_cep
        return ""

    @property
    def roles(self):
        """Property returning queryset of TipoContato for legacy compatibility."""
        return TipoContato.objects.filter(contatos_rel__contato=self, contatos_rel__ativo=True)

    def __str__(self):
        return self.nome_razao_social

# Alias
Contact = Contato


class ContatoTipo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='papeis_rel')
    tipo_contato = models.ForeignKey(TipoContato, on_delete=models.CASCADE, related_name='contatos_rel')
    principal = models.BooleanField('Papel Principal', default=False)
    data_inicio = models.DateField('Data de Início', default=timezone.now)
    data_fim = models.DateField('Data de Término', null=True, blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        unique_together = ('contato', 'tipo_contato')
        verbose_name = 'Papel do Contato'
        verbose_name_plural = 'Papéis do Contato'


class PessoaFisica(models.Model):
    contato = models.OneToOneField(Contato, on_delete=models.CASCADE, related_name='pessoa_fisica', primary_key=True)
    cpf = models.CharField('CPF', max_length=14, blank=True, null=True, unique=True)
    rg = models.CharField('RG', max_length=20, blank=True)
    orgao_emissor_rg = models.CharField('Órgão Emissor RG', max_length=20, blank=True)
    uf_rg = models.CharField('UF RG', max_length=2, blank=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    sexo = models.CharField('Sexo', max_length=20, blank=True)
    estado_civil = models.CharField('Estado Civil', max_length=30, blank=True)
    
    profissao = models.CharField('Profissão', max_length=100, blank=True)
    registro_profissional = models.CharField('Registro Profissional', max_length=50, blank=True)
    conselho_profissional = models.CharField('Conselho Profissional (ex: CREA)', max_length=50, blank=True)
    uf_conselho = models.CharField('UF Conselho', max_length=2, blank=True)
    especialidade = models.CharField('Especialidade', max_length=100, blank=True)
    
    nacionalidade = models.CharField('Nacionalidade', max_length=50, default='Brasileira', blank=True)
    naturalidade = models.CharField('Naturalidade', max_length=100, blank=True)
    
    email_pessoal = models.EmailField('E-mail Pessoal', blank=True)
    telefone_pessoal = models.CharField('Telefone Pessoal', max_length=30, blank=True)
    whatsapp = models.CharField('WhatsApp', max_length=30, blank=True)
    observacoes = models.TextField('Observações Pessoais', blank=True)

    class Meta:
        verbose_name = 'Pessoa Física'
        verbose_name_plural = 'Pessoas Físicas'

    @property
    def formatted_cpf(self):
        if not self.cpf:
            return ""
        d = re.sub(r'\D', '', str(self.cpf))
        if len(d) == 11:
            return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
        return self.cpf


class RegimeTributarioChoices(models.TextChoices):
    SIMPLES_NACIONAL = 'SIMPLES_NACIONAL', 'Simples Nacional'
    LUCRO_PRESUMIDO = 'LUCRO_PRESUMIDO', 'Lucro Presumido'
    LUCRO_REAL = 'LUCRO_REAL', 'Lucro Real'
    MEI = 'MEI', 'Microempreendedor Individual (MEI)'
    IMUNE = 'IMUNE', 'Imune'
    ISENTA = 'ISENTA', 'Isenta'
    NAO_INFORMADO = 'NAO_INFORMADO', 'Não Informado'

class IndicadorInscricaoEstadualChoices(models.TextChoices):
    CONTRIBUINTE = 'CONTRIBUINTE', '1 - Contribuinte ICMS'
    ISENTO = 'ISENTO', '2 - Contribuinte Isento de Inscrição'
    NAO_CONTRIBUINTE = 'NAO_CONTRIBUINTE', '9 - Não Contribuinte'
    NAO_INFORMADO = 'NAO_INFORMADO', 'Não Informado'

class SituacaoCadastralChoices(models.TextChoices):
    ATIVA = 'ATIVA', 'Ativa'
    BAIXADA = 'BAIXADA', 'Baixada'
    SUSPENSA = 'SUSPENSA', 'Suspensa'
    INAPTA = 'INAPTA', 'Inapta'
    NULA = 'NULA', 'Nula'
    NAO_INFORMADA = 'NAO_INFORMADA', 'Não Informada'


class PessoaJuridica(models.Model):
    contato = models.OneToOneField(Contato, on_delete=models.CASCADE, related_name='pessoa_juridica', primary_key=True)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True, null=True, unique=True)
    razao_social = models.CharField('Razão Social', max_length=255)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=255, blank=True)
    
    inscricao_estadual = models.CharField('Inscrição Estadual', max_length=30, blank=True)
    indicador_inscricao_estadual = models.CharField('Indicador de IE', max_length=30, choices=IndicadorInscricaoEstadualChoices.choices, default=IndicadorInscricaoEstadualChoices.NAO_INFORMADO)
    inscricao_municipal = models.CharField('Inscrição Municipal', max_length=30, blank=True)
    
    codigo_municipio = models.CharField('Código IBGE Município', max_length=10, blank=True)
    municipio = models.CharField('Município Fiscal', max_length=100, blank=True)
    uf = models.CharField('UF Fiscal', max_length=2, blank=True)
    
    natureza_juridica = models.CharField('Natureza Jurídica', max_length=100, blank=True)
    porte_empresa = models.CharField('Porte da Empresa', max_length=50, blank=True)
    cnae_principal = models.CharField('CNAE Principal', max_length=20, blank=True)
    cnaes_secundarios = models.TextField('CNAEs Secundários', blank=True)
    
    situacao_cadastral = models.CharField('Situação Cadastral', max_length=30, choices=SituacaoCadastralChoices.choices, default=SituacaoCadastralChoices.ATIVA)
    data_abertura = models.DateField('Data de Abertura', null=True, blank=True)
    
    regime_tributario = models.CharField('Regime Tributário', max_length=30, choices=RegimeTributarioChoices.choices, default=RegimeTributarioChoices.NAO_INFORMADO)
    optante_simples_nacional = models.BooleanField('Optante pelo Simples Nacional', default=False)
    optante_simei = models.BooleanField('Optante pelo SIMEI', default=False)
    incentivador_cultural = models.BooleanField('Incentivador Cultural', default=False)
    
    responsavel_legal = models.CharField('Responsável Legal', max_length=255, blank=True)
    email_comercial = models.EmailField('E-mail Comercial/Fiscal', blank=True)
    telefone_comercial = models.CharField('Telefone Comercial', max_length=30, blank=True)
    site = models.URLField('Site Oficial', blank=True)
    observacoes = models.TextField('Observações Empresariais', blank=True)

    class Meta:
        verbose_name = 'Pessoa Jurídica'
        verbose_name_plural = 'Pessoas Jurídicas'

    @property
    def formatted_cnpj(self):
        if not self.cnpj:
            return ""
        d = re.sub(r'\D', '', str(self.cnpj))
        if len(d) == 14:
            return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
        return self.cnpj


class TipoVinculoChoices(models.TextChoices):
    SOCIO = 'SOCIO', 'Sócio'
    ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
    RESPONSAVEL_LEGAL = 'RESPONSAVEL_LEGAL', 'Responsável Legal'
    CONTATO_COMERCIAL = 'CONTATO_COMERCIAL', 'Contato Comercial'
    CONTATO_FINANCEIRO = 'CONTATO_FINANCEIRO', 'Contato Financeiro'
    CONTATO_FISCAL = 'CONTATO_FISCAL', 'Contato Fiscal'
    CONTATO_OPERACIONAL = 'CONTATO_OPERACIONAL', 'Contato Operacional'
    PROCURADOR = 'PROCURADOR', 'Procurador'
    EMPREGADO = 'EMPREGADO', 'Empregado'
    PRESTADOR = 'PRESTADOR', 'Prestador de Serviço'
    REPRESENTANTE = 'REPRESENTANTE', 'Representante Comercial'
    OUTRO = 'OUTRO', 'Outro Vínculo'


class VinculoContato(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pessoa_fisica = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='vinculos_como_pf', limit_choices_to={'tipo_pessoa': TipoPessoaChoices.FISICA})
    pessoa_juridica = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='vinculos_como_pj', limit_choices_to={'tipo_pessoa': TipoPessoaChoices.JURIDICA})
    
    tipo_vinculo = models.CharField('Tipo de Vínculo', max_length=50, choices=TipoVinculoChoices.choices, default=TipoVinculoChoices.CONTATO_COMERCIAL)
    cargo = models.CharField('Cargo', max_length=100, blank=True)
    departamento = models.CharField('Departamento', max_length=100, blank=True)
    
    email_corporativo = models.EmailField('E-mail Corporativo', blank=True)
    telefone_corporativo = models.CharField('Telefone Corporativo', max_length=30, blank=True)
    ramal = models.CharField('Ramal', max_length=10, blank=True)
    
    principal = models.BooleanField('Vínculo Principal', default=False)
    responsavel_legal = models.BooleanField('É Responsável Legal', default=False)
    representante_comercial = models.BooleanField('É Representante Comercial', default=False)
    pode_assinar = models.BooleanField('Pode Assinar Documentos', default=False)
    pode_receber_documentos = models.BooleanField('Pode Receber Documentos', default=False)
    pode_receber_cobrancas = models.BooleanField('Pode Receber Cobranças', default=False)
    
    data_inicio = models.DateField('Data de Início', default=timezone.now)
    data_fim = models.DateField('Data de Término', null=True, blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Vínculo de Contato (PF x PJ)'
        verbose_name_plural = 'Vínculos de Contatos (PF x PJ)'

    def __str__(self):
        return f"{self.pessoa_fisica.nome_razao_social} @ {self.pessoa_juridica.nome_razao_social} ({self.get_tipo_vinculo_display()})"


class Endereco(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logradouro = models.CharField('Logradouro', max_length=255)
    numero = models.CharField('Número', max_length=20, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cep = models.CharField('CEP', max_length=10, blank=True)
    
    codigo_municipio = models.CharField('Código IBGE Município', max_length=10, blank=True)
    municipio = models.CharField('Município', max_length=100, blank=True)
    uf = models.CharField('UF', max_length=2, blank=True)
    pais = models.CharField('País', max_length=50, default='Brasil')
    
    referencia = models.CharField('Ponto de Referência', max_length=255, blank=True)
    latitude = models.DecimalField('Latitude', max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField('Longitude', max_digits=11, decimal_places=8, null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    @property
    def format_address(self):
        num_str = f", {self.numero}" if self.numero else ""
        bairro_str = f" - {self.bairro}" if self.bairro else ""
        return f"{self.logradouro}{num_str}{bairro_str}"

    @property
    def formatted_cep(self):
        if not self.cep:
            return ""
        d = re.sub(r'\D', '', str(self.cep))
        if len(d) == 8:
            return f"{d[:5]}-{d[5:]}"
        return self.cep


class TipoEnderecoChoices(models.TextChoices):
    RESIDENCIAL = 'RESIDENCIAL', 'Residencial'
    COMERCIAL = 'COMERCIAL', 'Comercial'
    FISCAL = 'FISCAL', 'Fiscal'
    COBRANCA = 'COBRANCA', 'Cobrança'
    ENTREGA = 'ENTREGA', 'Entrega'
    PRESTACAO_SERVICO = 'PRESTACAO_SERVICO', 'Prestação de Serviço'
    OUTRO = 'OUTRO', 'Outro'


class ContatoEndereco(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='enderecos')
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, related_name='contatos')
    tipo_endereco = models.CharField('Tipo de Endereço', max_length=50, choices=TipoEnderecoChoices.choices, default=TipoEnderecoChoices.COMERCIAL)
    
    principal = models.BooleanField('Endereço Principal', default=False)
    correspondencia = models.BooleanField('Para Correspondência', default=False)
    cobranca = models.BooleanField('Para Cobrança', default=False)
    entrega = models.BooleanField('Para Entrega', default=False)
    fiscal = models.BooleanField('Endereço Fiscal', default=False)
    prestacao_servico = models.BooleanField('Para Prestação de Serviço', default=False)
    
    data_inicio = models.DateField('Data de Início', default=timezone.now)
    data_fim = models.DateField('Data de Término', null=True, blank=True)

    class Meta:
        verbose_name = 'Endereço do Contato'
        verbose_name_plural = 'Endereços dos Contatos'


class TipoTelefoneChoices(models.TextChoices):
    CELULAR = 'CELULAR', 'Celular'
    FIXO = 'FIXO', 'Fixo'
    COMERCIAL = 'COMERCIAL', 'Comercial'
    RESIDENCIAL = 'RESIDENCIAL', 'Residencial'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
    OUTRO = 'OUTRO', 'Outro'


class ContatoTelefone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='telefones')
    numero = models.CharField('Número do Telefone', max_length=30)
    tipo = models.CharField('Tipo', max_length=30, choices=TipoTelefoneChoices.choices, default=TipoTelefoneChoices.CELULAR)
    
    principal = models.BooleanField('Telefone Principal', default=False)
    whatsapp = models.BooleanField('É WhatsApp', default=False)
    ramal = models.CharField('Ramal', max_length=10, blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Telefone do Contato'
        verbose_name_plural = 'Telefones dos Contatos'


class TipoEmailChoices(models.TextChoices):
    PESSOAL = 'PESSOAL', 'Pessoal'
    COMERCIAL = 'COMERCIAL', 'Comercial'
    FINANCEIRO = 'FINANCEIRO', 'Financeiro'
    FISCAL = 'FISCAL', 'Fiscal'
    COBRANCA = 'COBRANCA', 'Cobrança'
    DOCUMENTOS = 'DOCUMENTOS', 'Documentos Técnicos'
    OUTRO = 'OUTRO', 'Outro'


class ContatoEmail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField('E-mail')
    tipo = models.CharField('Tipo', max_length=30, choices=TipoEmailChoices.choices, default=TipoEmailChoices.COMERCIAL)
    
    principal = models.BooleanField('E-mail Principal', default=False)
    recebe_documentos = models.BooleanField('Recebe Documentos', default=False)
    recebe_cobranca = models.BooleanField('Recebe Cobranças', default=False)
    recebe_comunicados = models.BooleanField('Recebe Comunicados', default=False)
    recebe_integracoes = models.BooleanField('Recebe Integrações', default=False)
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'E-mail do Contato'
        verbose_name_plural = 'E-mails dos Contatos'


class ContatoComercial(models.Model):
    contato = models.OneToOneField(Contato, on_delete=models.CASCADE, related_name='dados_comerciais', primary_key=True)
    codigo_externo = models.CharField('Código Externo ERP/CRM', max_length=50, blank=True)
    limite_credito = models.DecimalField('Limite de Crédito (R$)', max_digits=12, decimal_places=2, default=0.00)
    condicao_pagamento = models.CharField('Condição Padrão de Pagamento', max_length=100, blank=True)
    prazo_pagamento_dias = models.PositiveIntegerField('Prazo de Pagamento (Dias)', default=30)
    forma_pagamento_preferencial = models.CharField('Forma Preferencial de Pagamento', max_length=50, blank=True)
    
    banco = models.CharField('Banco', max_length=50, blank=True)
    agencia = models.CharField('Agência', max_length=20, blank=True)
    conta = models.CharField('Conta Bancária', max_length=30, blank=True)
    tipo_conta = models.CharField('Tipo de Conta', max_length=20, blank=True)
    pix = models.CharField('Chave Pix', max_length=255, blank=True)
    
    classificacao_risco = models.CharField('Classificação de Risco', max_length=20, blank=True, default='BAIXO')
    vendedor_responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='contatos_comerciais')
    centro_custo = models.CharField('Centro de Custo', max_length=50, blank=True)
    categoria_financeira = models.CharField('Categoria Financeira', max_length=50, blank=True)
    observacoes_financeiras = models.TextField('Observações Financeiras e Bancárias', blank=True)

    class Meta:
        verbose_name = 'Dados Comerciais & Bancários'
        verbose_name_plural = 'Dados Comerciais & Bancários'


class EsferaPublicaChoices(models.TextChoices):
    MUNICIPAL = 'MUNICIPAL', 'Municipal'
    ESTADUAL = 'ESTADUAL', 'Estadual'
    FEDERAL = 'FEDERAL', 'Federal'
    OUTRA = 'OUTRA', 'Outra'

class PoderPublicoChoices(models.TextChoices):
    EXECUTIVO = 'EXECUTIVO', 'Executivo'
    LEGISLATIVO = 'LEGISLATIVO', 'Legislativo'
    JUDICIARIO = 'JUDICIARIO', 'Judiciário'
    MINISTERIO_PUBLICO = 'MINISTERIO_PUBLICO', 'Ministério Público'
    TRIBUNAL_DE_CONTAS = 'TRIBUNAL_DE_CONTAS', 'Tribunal de Contas'
    OUTRO = 'OUTRO', 'Outro'


class OrgaoPublico(models.Model):
    contato = models.OneToOneField(Contato, on_delete=models.CASCADE, related_name='orgao_publico', primary_key=True)
    esfera = models.CharField('Esfera', max_length=20, choices=EsferaPublicaChoices.choices, default=EsferaPublicaChoices.MUNICIPAL)
    poder = models.CharField('Poder', max_length=30, choices=PoderPublicoChoices.choices, default=PoderPublicoChoices.EXECUTIVO)
    orgao_superior = models.CharField('Órgão Superior', max_length=255, blank=True)
    
    codigo_unidade_gestora = models.CharField('Código UG', max_length=50, blank=True)
    codigo_siasg = models.CharField('Código SIASG', max_length=50, blank=True)
    codigo_ug = models.CharField('Código Unidade Gestora', max_length=50, blank=True)
    unidade_administrativa = models.CharField('Unidade Administrativa', max_length=255, blank=True)
    
    responsavel_contrato = models.CharField('Responsável pelo Contrato', max_length=255, blank=True)
    email_fiscal_contrato = models.EmailField('E-mail Fiscal do Contrato', blank=True)
    
    exige_retencao = models.BooleanField('Exige Retenção na Fonte', default=True)
    exige_empenho = models.BooleanField('Exige Nota de Empenho', default=True)
    numero_empenho = models.CharField('Número do Empenho', max_length=50, blank=True)
    processo_administrativo = models.CharField('Processo Administrativo', max_length=100, blank=True)
    observacoes = models.TextField('Observações de Licitação e Empenho', blank=True)

    class Meta:
        verbose_name = 'Órgão Público'
        verbose_name_plural = 'Órgãos Públicos'


class StatusEmpreendimentoChoices(models.TextChoices):
    PLANEJADO = 'PLANEJADO', 'Planejado'
    EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
    PAUSADO = 'PAUSADO', 'Pausado'
    CONCLUIDO = 'CONCLUIDO', 'Concluído'
    CANCELADO = 'CANCELADO', 'Cancelado'
    ARQUIVADO = 'ARQUIVADO', 'Arquivado'


class Empreendimento(models.Model):
    contato = models.OneToOneField(Contato, on_delete=models.CASCADE, related_name='empreendimento', primary_key=True)
    codigo_interno = models.CharField('Código Interno', max_length=50, blank=True)
    descricao = models.TextField('Descrição do Empreendimento', blank=True)
    tipo_empreendimento = models.CharField('Tipo de Empreendimento', max_length=100, blank=True)
    
    data_inicio = models.DateField('Data de Início', null=True, blank=True)
    data_prevista_termino = models.DateField('Data Prevista de Término', null=True, blank=True)
    data_termino = models.DateField('Data de Término Efetiva', null=True, blank=True)
    
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='empreendimentos_gerenciados')
    cliente_principal = models.ForeignKey(Contato, on_delete=models.SET_NULL, null=True, blank=True, related_name='empreendimentos_cliente')
    endereco = models.CharField('Endereço do Empreendimento', max_length=255, blank=True)
    status = models.CharField('Status', max_length=30, choices=StatusEmpreendimentoChoices.choices, default=StatusEmpreendimentoChoices.EM_ANDAMENTO)
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Empreendimento'
        verbose_name_plural = 'Empreendimentos'


# Legacy Interaction Model preserved
class InteractionTypeChoices(models.TextChoices):
    REUNIAO = 'REUNIAO', 'Reunião'
    LIGACAO = 'LIGACAO', 'Ligação'
    EMAIL = 'EMAIL', 'E-mail'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
    VISITA = 'VISITA', 'Visita Técnica'
    OUTRO = 'OUTRO', 'Outro'


class Interaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='interactions', verbose_name='Contato')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='interactions', verbose_name='Usuário Responsável')
    date = models.DateTimeField('Data e Hora', default=timezone.now)
    interaction_type = models.CharField('Tipo', max_length=50, choices=InteractionTypeChoices.choices, default=InteractionTypeChoices.REUNIAO)
    subject = models.CharField('Assunto', max_length=255)
    description = models.TextField('Descrição')
    
    next_action = models.CharField('Próxima Ação', max_length=255, blank=True)
    next_action_deadline = models.DateField('Prazo da Próxima Ação', null=True, blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Interação'
        verbose_name_plural = 'Interações'

    def __str__(self):
        return f"{self.get_interaction_type_display()} - {self.subject} ({self.contact.nome_razao_social})"
