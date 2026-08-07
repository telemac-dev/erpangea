from django.db import models
from django.conf import settings
from django.utils import timezone
from contacts.models import Contact
from commercial.models import Contract, ServiceTypeChoices

class ProjectStatusChoices(models.TextChoices):
    EM_ELABORACAO = 'EM_ELABORACAO', 'Em Elaboração'
    EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
    EM_REVISAO = 'EM_REVISAO', 'Em Revisão'
    AGUARDANDO_APROVACAO = 'AGUARDANDO_APROVACAO', 'Aguardando Aprovação'
    PARALISADO = 'PARALISADO', 'Paralisado'
    CONCLUIDO = 'CONCLUIDO', 'Concluído'
    CANCELADO = 'CANCELADO', 'Cancelado'

class TaskStatusChoices(models.TextChoices):
    PENDENTE = 'PENDENTE', 'Pendente'
    EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
    EM_REVISAO = 'EM_REVISAO', 'Em Revisão'
    CONCLUIDA = 'CONCLUIDA', 'Concluída'
    CANCELADA = 'CANCELADA', 'Cancelada'

class DeliveryStatusChoices(models.TextChoices):
    RASCUNHO = 'RASCUNHO', 'Rascunho'
    AGUARDANDO_APROVACAO = 'AGUARDANDO_APROVACAO', 'Aguardando Aprovação'
    APROVADO = 'APROVADO', 'Aprovado'
    REJEITADO = 'REJEITADO', 'Rejeitado'


class Project(models.Model):
    code = models.CharField('Código do Projeto', max_length=50, unique=True)
    name = models.CharField('Nome do Projeto', max_length=255)
    client = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='projects', verbose_name='Cliente')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name='Contrato de Origem')
    
    service_type = models.CharField('Tipo de Serviço', max_length=50, choices=ServiceTypeChoices.choices, default=ServiceTypeChoices.GEOTECNIA)
    description = models.TextField('Descrição do Projeto')
    
    technical_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='technical_projects', verbose_name='Responsável Técnico (RT)')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects', verbose_name='Gerente de Projeto')
    
    site_address = models.CharField('Endereço da Obra', max_length=255, blank=True)
    city = models.CharField('Município', max_length=100, blank=True)
    state = models.CharField('UF', max_length=2, blank=True)
    
    start_date = models.DateField('Data de Início')
    expected_completion_date = models.DateField('Data Prevista de Conclusão')
    actual_completion_date = models.DateField('Data Efetiva de Conclusão', null=True, blank=True)
    
    status = models.CharField('Status', max_length=50, choices=ProjectStatusChoices.choices, default=ProjectStatusChoices.EM_ANDAMENTO)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_delayed(self):
        """Verifica se o projeto está atrasado conforme regra do dashboard."""
        if self.status != ProjectStatusChoices.CONCLUIDO and self.expected_completion_date:
            return self.expected_completion_date < timezone.now().date()
        return False


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name='Projeto')
    name = models.CharField('Nome da Tarefa / Etapa', max_length=255)
    description = models.TextField('Descrição', blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='Responsável')
    due_date = models.DateField('Prazo de Conclusão', null=True, blank=True)
    status = models.CharField('Status', max_length=50, choices=TaskStatusChoices.choices, default=TaskStatusChoices.PENDENTE)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'

    def __str__(self):
        return f"{self.name} ({self.project.code})"


class Delivery(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='deliveries', verbose_name='Projeto')
    title = models.CharField('Título da Entrega', max_length=255)
    description = models.TextField('Descrição dos Documentos / Relatórios', blank=True)
    delivery_date = models.DateField('Data da Entrega', default=timezone.now)
    delivered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries', verbose_name='Entregue por')
    status = models.CharField('Status de Aprovação', max_length=50, choices=DeliveryStatusChoices.choices, default=DeliveryStatusChoices.AGUARDANDO_APROVACAO)
    notes = models.TextField('Observações do Cliente / Parecer', blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        ordering = ['-delivery_date']
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'

    def __str__(self):
        return f"{self.title} - {self.project.code}"
