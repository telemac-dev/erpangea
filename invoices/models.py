from django.db import models
from django.core.exceptions import ValidationError
from measurements.models import MeasurementSheet, MeasurementStatusEnum
from datetime import timedelta, date

class InvoiceStatusEnum(models.TextChoices):
    SOLICITADA = 'SOLICITADA', 'Solicitada'
    EMITIDA = 'EMITIDA', 'Emitida'
    PAGA = 'PAGA', 'Paga'
    CANCELADA = 'CANCELADA', 'Cancelada'

class ReceivableStatusEnum(models.TextChoices):
    A_VENCER = 'A_VENCER', 'A Vencer'
    VENCIDA = 'VENCIDA', 'Vencida'
    LIQUIDADA = 'LIQUIDADA', 'Liquidada'

class ServiceInvoice(models.Model):
    medicao = models.OneToOneField(MeasurementSheet, on_delete=models.PROTECT, related_name='invoice')
    numero_nfse = models.CharField(max_length=30, unique=True)
    codigo_verificacao = models.CharField(max_length=50, blank=True)
    data_emissao = models.DateField(default=date.today)
    valor_bruto = models.DecimalField(max_digits=12, decimal_places=2)
    aliquota_iss = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    retencoes_federais = models.JSONField(default=dict, blank=True) # {PIS: ..., COFINS: ..., INSS: ..., CSLL: ..., IRRF: ...}
    valor_liquido = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=InvoiceStatusEnum.choices, default=InvoiceStatusEnum.EMITIDA)
    arquivo_xml = models.FileField(upload_to='invoices/xml/', null=True, blank=True)
    arquivo_pdf = models.FileField(upload_to='invoices/pdf/', null=True, blank=True)

    def clean(self):
        # Regra de negócio: Apenas medições com status "Aprovada pelo Cliente" ficam disponíveis para seleção/emissão
        if self.medicao_id:
            # Se for nova emissão, a medição deve estar APROVADA_CLIENTE
            if not self.pk and self.medicao.status != MeasurementStatusEnum.APROVADA_CLIENTE:
                raise ValidationError(
                    f"A medição selecionada está com status '{self.medicao.get_status_display()}'. "
                    f"Apenas medições com status 'Aprovada pelo Cliente' podem ser faturadas."
                )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.clean()
        
        # Calcula valor líquido se não calculado
        if not self.valor_liquido and self.valor_bruto:
            total_retencoes = sum(float(v) for v in self.retencoes_federais.values()) if self.retencoes_federais else 0.0
            desconto_iss = float(self.valor_bruto) * (float(self.aliquota_iss) / 100.0)
            self.valor_liquido = float(self.valor_bruto) - desconto_iss - total_retencoes
            
        super().save(*args, **kwargs)
        
        # Ao emitir uma NFS-e nova, gera as parcelas a receber e atualiza a medição para FATURADA
        if is_new and self.status == InvoiceStatusEnum.EMITIDA:
            self.medicao.status = MeasurementStatusEnum.FATURADA
            self.medicao.save(update_fields=['status'])
            
            # Gera parcela padrão em 30 dias
            AccountReceivable.objects.create(
                nota_fiscal=self,
                numero_parcela=1,
                data_vencimento=self.data_emissao + timedelta(days=30),
                valor_parcela=self.valor_liquido,
                status=ReceivableStatusEnum.A_VENCER
            )

    def cancel_invoice(self):
        # Regra de negócio: Cancelamento cancela contas a receber e estorna medição para APROVADA_CLIENTE
        self.status = InvoiceStatusEnum.CANCELADA
        self.save(update_fields=['status'])
        
        # Remove ou cancela recebíveis
        self.receivables.all().delete()
        
        # Estorna medição
        self.medicao.status = MeasurementStatusEnum.APROVADA_CLIENTE
        self.medicao.save(update_fields=['status'])

    def __str__(self):
        return f"NFS-e {self.numero_nfse} - R$ {self.valor_liquido} ({self.get_status_display()})"

class AccountReceivable(models.Model):
    nota_fiscal = models.ForeignKey(ServiceInvoice, on_delete=models.CASCADE, related_name='receivables')
    numero_parcela = models.PositiveIntegerField(default=1)
    data_vencimento = models.DateField()
    data_recebimento = models.DateField(null=True, blank=True)
    valor_parcela = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=ReceivableStatusEnum.choices, default=ReceivableStatusEnum.A_VENCER)

    class Meta:
        ordering = ['data_vencimento']

    def __str__(self):
        return f"Parcela {self.numero_parcela} (NFS-e {self.nota_fiscal.numero_nfse}) - R$ {self.valor_parcela} [{self.get_status_display()}]"
