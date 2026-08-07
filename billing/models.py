from django.db import models
from django.conf import settings
from django.utils import timezone
from contacts.models import Contact
from commercial.models import Contract
from measurements.models import Measurement

class InvoiceStatusChoices(models.TextChoices):
    EM_ABERTO = 'EM_ABERTO', 'Em Aberto'
    PAGO = 'PAGO', 'Pago'
    PARCIALMENTE_PAGO = 'PARCIALMENTE_PAGO', 'Parcialmente Pago'
    ATRASADO = 'ATRASADO', 'Atrasado'
    CANCELADO = 'CANCELADO', 'Cancelado'


class Invoice(models.Model):
    invoice_number = models.CharField('Número da NF / Fatura', max_length=50, unique=True)
    client = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='invoices', verbose_name='Cliente')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', verbose_name='Contrato de Origem')
    measurement = models.ForeignKey(Measurement, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', verbose_name='Medição de Origem')
    
    issue_date = models.DateField('Data de Emissão', default=timezone.now)
    due_date = models.DateField('Data de Vencimento')
    payment_date = models.DateField('Data do Pagamento', null=True, blank=True)
    
    amount = models.DecimalField('Valor Faturado (R$)', max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField('Valor Recebido (R$)', max_digits=12, decimal_places=2, default=0.00)
    
    status = models.CharField('Status do Pagamento', max_length=50, choices=InvoiceStatusChoices.choices, default=InvoiceStatusChoices.EM_ABERTO)
    notes = models.TextField('Observações', blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-due_date', '-created_at']
        verbose_name = 'Fatura / Nota Fiscal'
        verbose_name_plural = 'Faturas / Notas Fiscais'

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name} (R$ {self.amount})"

    @property
    def is_overdue(self):
        """Verifica se a fatura está atrasada."""
        if self.status == InvoiceStatusChoices.EM_ABERTO and self.due_date:
            return self.due_date < timezone.now().date()
        return False
