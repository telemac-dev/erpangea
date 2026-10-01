from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
from contacts.models import Contact
from projects.models import Project

class CostCenterEnum(models.TextChoices):
    ADMINISTRATIVO = 'ADMINISTRATIVO', 'Administrativo'
    OPERACIONAL_GEOTECNIA = 'OPERACIONAL_GEOTECNIA', 'Operacional Geotécnico'
    COMERCIAL = 'COMERCIAL', 'Comercial'
    TI_SOFTWARES = 'TI_SOFTWARES', 'TI & Softwares'

class PayableStatusEnum(models.TextChoices):
    AGUARDANDO_APROVACAO = 'AGUARDANDO_APROVACAO', 'Aguardando Aprovação'
    APROVADA = 'APROVADA', 'Aprovada'
    LIQUIDADA = 'LIQUIDADA', 'Liquidada'
    CANCELADA = 'CANCELADA', 'Cancelada'

class AccountPayable(models.Model):
    fornecedor = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name='payables')
    projeto = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    centro_de_custo = models.CharField(max_length=30, choices=CostCenterEnum.choices, default=CostCenterEnum.ADMINISTRATIVO)
    categoria_despesa = models.CharField(max_length=100, help_text="Ex: Laboratório de Solos, Combustível, Softwares")
    descricao = models.CharField(max_length=255)
    valor_nominal = models.DecimalField(max_digits=12, decimal_places=2)
    data_vencimento = models.DateField(db_index=True)
    data_pagamento = models.DateField(null=True, blank=True)
    comprovante_fiscal = models.FileField(upload_to='financial/fiscal/', null=True, blank=True)
    comprovante_pagamento = models.FileField(upload_to='financial/payments/', null=True, blank=True)
    status = models.CharField(max_length=25, choices=PayableStatusEnum.choices, default=PayableStatusEnum.APROVADA)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['data_vencimento']

    def clean(self):
        # Regra 1: Despesas superiores a R$ 5.000,00 ficam retidas até autorização
        if self.valor_nominal and self.valor_nominal > Decimal('5000.00'):
            # Se for criação nova ou se ainda não foi explicitamente aprovada/liquidada por alçada
            if not self.pk and self.status != PayableStatusEnum.AGUARDANDO_APROVACAO:
                self.status = PayableStatusEnum.AGUARDANDO_APROVACAO

        # Regra 2: Toda conta liquidada exige comprovante bancário e data de pagamento
        if self.status == PayableStatusEnum.LIQUIDADA:
            if not self.comprovante_pagamento:
                raise ValidationError("Toda conta liquidada exige o anexo obrigatório do comprovante bancário de pagamento.")
            if not self.data_pagamento:
                raise ValidationError("É obrigatório informar a data de pagamento para liquidar a despesa.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor_nominal} [{self.get_status_display()}]"
