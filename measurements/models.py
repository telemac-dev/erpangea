from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from commercial.models import Contract

class MeasurementStatusEnum(models.TextChoices):
    RASCUNHO = 'RASCUNHO', 'Rascunho'
    SUBMETIDA_TECNICO = 'SUBMETIDA_TECNICO', 'Submetida pelo Técnico'
    APROVADA_CLIENTE = 'APROVADA_CLIENTE', 'Aprovada pelo Cliente'
    REJEITADA = 'REJEITADA', 'Rejeitada'
    FATURADA = 'FATURADA', 'Faturada'

class MeasurementSheet(models.Model):
    contrato = models.ForeignKey(Contract, on_delete=models.PROTECT, related_name='measurements')
    numero_medicao = models.PositiveIntegerField(blank=True)
    competencia = models.DateField(help_text="Mês/Ano de referência")
    valor_total_medido = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=25, choices=MeasurementStatusEnum.choices, default=MeasurementStatusEnum.RASCUNHO)
    documento_comprovatorio = models.FileField(upload_to='measurements/', null=True, blank=True)

    class Meta:
        unique_together = ('contrato', 'numero_medicao')
        ordering = ['contrato', 'numero_medicao']

    def clean(self):
        # Regra de negócio: O somatório das medições parciais não pode ultrapassar o saldo financeiro do contrato
        if self.contrato_id and self.valor_total_medido:
            outras_medicoes = MeasurementSheet.objects.filter(
                contrato=self.contrato
            ).exclude(status=MeasurementStatusEnum.REJEITADA)
            
            if self.pk:
                outras_medicoes = outras_medicoes.exclude(pk=self.pk)
                
            total_acumulado = outras_medicoes.aggregate(total=Sum('valor_total_medido'))['total'] or 0
            if total_acumulado + self.valor_total_medido > self.contrato.valor_total_contratado:
                saldo_disponivel = self.contrato.valor_total_contratado - total_acumulado
                raise ValidationError(
                    f"O valor medido (R$ {self.valor_total_medido}) ultrapassa o saldo disponível do contrato (R$ {saldo_disponivel}). "
                    f"Total contratado: R$ {self.contrato.valor_total_contratado}."
                )

    def save(self, *args, **kwargs):
        if not self.numero_medicao:
            ultimo = MeasurementSheet.objects.filter(contrato=self.contrato).aggregate(models.Max('numero_medicao'))['numero_medicao__max'] or 0
            self.numero_medicao = ultimo + 1
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contrato.numero_contrato} - Medição #{self.numero_medicao:02d} ({self.get_status_display()})"

class MeasurementItem(models.Model):
    folha_medicao = models.ForeignKey(MeasurementSheet, on_delete=models.CASCADE, related_name='items')
    discriminacao = models.CharField(max_length=255)
    percentual_executado = models.DecimalField(max_digits=5, decimal_places=2)
    valor_apurado = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.discriminacao} ({self.percentual_executado}%) - R$ {self.valor_apurado}"
