from django.db import models
from django.conf import settings
from django.utils import timezone
from projects.models import Project
from commercial.models import Contract

class MeasurementStatusChoices(models.TextChoices):
    EM_ELABORACAO = 'EM_ELABORACAO', 'Em Elaboração'
    EM_REVISAO = 'EM_REVISAO', 'Em Revisão'
    AGUARDANDO_APROVACAO = 'AGUARDANDO_APROVACAO', 'Aguardando Aprovação'
    APROVADA = 'APROVADA', 'Aprovada'
    REJEITADA = 'REJEITADA', 'Rejeitada'
    CANCELADA = 'CANCELADA', 'Cancelada'


class Measurement(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='measurements', verbose_name='Projeto')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='measurements', verbose_name='Contrato de Origem')
    
    number = models.CharField('Número da Medição', max_length=50)
    measurement_date = models.DateField('Data da Medição', default=timezone.now)
    period_start = models.DateField('Período de Referência - Início')
    period_end = models.DateField('Período de Referência - Fim')
    
    measured_value = models.DecimalField('Valor Medido (R$)', max_digits=12, decimal_places=2)
    percentage_completed = models.DecimalField('% Concluído da Etapa', max_digits=5, decimal_places=2, default=100.00)
    description = models.TextField('Descrição dos Serviços Medidos')
    
    status = models.CharField('Status da Medição', max_length=50, choices=MeasurementStatusChoices.choices, default=MeasurementStatusChoices.EM_ELABORACAO)
    
    measured_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='measured_items', verbose_name='Medido por')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_measurements', verbose_name='Aprovado por')
    approval_date = models.DateTimeField('Data de Aprovação', null=True, blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-measurement_date', '-created_at']
        verbose_name = 'Medição'
        verbose_name_plural = 'Medições'

    def __str__(self):
        return f"{self.number} - {self.project.code} (R$ {self.measured_value})"
