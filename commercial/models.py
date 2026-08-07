from django.db import models
from django.conf import settings
from contacts.models import Contact

class ServiceTypeChoices(models.TextChoices):
    GEOTECNIA = 'GEOTECNIA', 'Projetos e Consultoria em Geotecnia'
    FUNDACOES = 'FUNDACOES', 'Projetos de Fundação'
    CONTENCOES = 'CONTENCOES', 'Soluções de Contenção'
    MUROS = 'MUROS', 'Muros de Arrimo'
    OBRAS_TERRA = 'OBRAS_TERRA', 'Obras de Terra'
    ESTRUTURAS = 'ESTRUTURAS', 'Estruturas'
    PAVIMENTACAO = 'PAVIMENTACAO', 'Pavimentação'
    CONSULTORIA = 'CONSULTORIA', 'Consultoria Técnica'

class LeadStageChoices(models.TextChoices):
    NOVO = 'NOVO', 'Novo'
    QUALIFICACAO = 'QUALIFICACAO', 'Qualificação'
    CONTATO_REALIZADO = 'CONTATO_REALIZADO', 'Contato Realizado'
    PROPOSTA_EM_PREPARACAO = 'PROPOSTA_EM_PREPARACAO', 'Proposta em Preparação'
    CONVERTIDO = 'CONVERTIDO', 'Convertido'
    PERDIDO = 'PERDIDO', 'Perdido'

class ProposalStatusChoices(models.TextChoices):
    RASCUNHO = 'RASCUNHO', 'Rascunho'
    EM_REVISAO = 'EM_REVISAO', 'Em Revisão'
    ENVIADA = 'ENVIADA', 'Enviada'
    EM_NEGOCIACAO = 'EM_NEGOCIACAO', 'Em Negociação'
    APROVADA = 'APROVADA', 'Aprovada'
    RECUSADA = 'RECUSADA', 'Recusada'
    EXPIRADA = 'EXPIRADA', 'Expirada'
    CANCELADA = 'CANCELADA', 'Cancelada'

class ContractStatusChoices(models.TextChoices):
    EM_ELABORACAO = 'EM_ELABORACAO', 'Em Elaboração'
    EM_REVISAO = 'EM_REVISAO', 'Em Revisão'
    AGUARDANDO_ASSINATURA = 'AGUARDANDO_ASSINATURA', 'Aguardando Assinatura'
    ASSINADO = 'ASSINADO', 'Assinado'
    ATIVO = 'ATIVO', 'Ativo'
    SUSPENSO = 'SUSPENSO', 'Suspenso'
    ENCERRADO = 'ENCERRADO', 'Encerrado'
    RESCINDIDO = 'RESCINDIDO', 'Rescindido'


class Lead(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='leads', verbose_name='Contato / Cliente')
    source = models.CharField('Origem do Lead', max_length=100, blank=True)
    service_of_interest = models.CharField('Serviço de Interesse', max_length=50, choices=ServiceTypeChoices.choices, default=ServiceTypeChoices.GEOTECNIA)
    description = models.TextField('Descrição da Oportunidade')
    
    estimated_value = models.DecimalField('Valor Estimado (R$)', max_digits=12, decimal_places=2, null=True, blank=True)
    probability = models.PositiveIntegerField('Probabilidade (%)', default=50)
    
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads', verbose_name='Responsável Comercial')
    stage = models.CharField('Estágio', max_length=50, choices=LeadStageChoices.choices, default=LeadStageChoices.NOVO)
    expected_closing_date = models.DateField('Previsão de Fechamento', null=True, blank=True)
    notes = models.TextField('Observações', blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead / Oportunidade'
        verbose_name_plural = 'Leads / Oportunidades'

    def __str__(self):
        return f"{self.contact.name} - {self.get_service_of_interest_display()}"


class Proposal(models.Model):
    number = models.CharField('Número da Proposta', max_length=50)
    version = models.PositiveIntegerField('Versão', default=1)
    parent_proposal = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_versions', verbose_name='Versão Anterior')
    
    client = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='proposals', verbose_name='Cliente')
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='proposals', verbose_name='Lead de Origem')
    
    scope = models.TextField('Escopo do Projeto')
    included_services = models.TextField('Serviços Incluídos', blank=True)
    exclusions = models.TextField('Exclusões de Escopo', blank=True)
    assumptions = models.TextField('Premissas Técnicas', blank=True)
    
    execution_period_days = models.PositiveIntegerField('Prazo de Execução (Dias)', default=30)
    validity_days = models.PositiveIntegerField('Validade da Proposta (Dias)', default=30)
    total_value = models.DecimalField('Valor Total (R$)', max_digits=12, decimal_places=2)
    payment_terms = models.TextField('Condições de Pagamento', blank=True)
    
    technical_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='technical_proposals', verbose_name='Responsável Técnico (RT)')
    commercial_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='commercial_proposals', verbose_name='Responsável Comercial')
    
    status = models.CharField('Status', max_length=50, choices=ProposalStatusChoices.choices, default=ProposalStatusChoices.RASCUNHO)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at', '-version']
        verbose_name = 'Proposta Técnica'
        verbose_name_plural = 'Propostas Técnicas'

    def __str__(self):
        return f"{self.number} v{self.version} - {self.client.name}"


class Contract(models.Model):
    number = models.CharField('Número do Contrato', max_length=50, unique=True)
    client = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='contracts', verbose_name='Cliente')
    proposal = models.ForeignKey(Proposal, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts', verbose_name='Proposta de Origem')
    
    start_date = models.DateField('Data de Início')
    end_date = models.DateField('Data de Término', null=True, blank=True)
    total_value = models.DecimalField('Valor Total (R$)', max_digits=12, decimal_places=2)
    payment_terms = models.TextField('Condições de Pagamento', blank=True)
    readjustment_index = models.CharField('Índice de Reajuste', max_length=50, blank=True, default='IPCA')
    
    status = models.CharField('Status', max_length=50, choices=ContractStatusChoices.choices, default=ContractStatusChoices.EM_ELABORACAO)
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts', verbose_name='Gestor do Contrato')
    notes = models.TextField('Observações', blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    def __str__(self):
        return f"{self.number} - {self.client.name}"
