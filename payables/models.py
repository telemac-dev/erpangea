from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from contacts.models import Contact
from projects.models import Project

class BillCategoryChoices(models.TextChoices):
    MATERIAIS_OBRA = 'MATERIAIS_OBRA', 'Insumos / Materiais de Obra'
    LABORATORIO_ENSAIOS = 'LABORATORIO_ENSAIOS', 'Laboratório / Ensaios de Solo'
    EQUIPAMENTOS = 'EQUIPAMENTOS', 'Equipamentos / Aluguel de Maquinário'
    SUBCONTRATADOS = 'SUBCONTRATADOS', 'Subcontratados / Serviços Técnicos'
    IMPOSTOS_TAXAS = 'IMPOSTOS_TAXAS', 'Impostos / Taxas / ART'
    UTILIDADES_ESCRITORIO = 'UTILIDADES_ESCRITORIO', 'Utilidades / Despesas de Escritório'
    OUTROS = 'OUTROS', 'Outras Despesas'

class BillStatusChoices(models.TextChoices):
    EM_ABERTO = 'EM_ABERTO', 'Em Aberto'
    PAGO = 'PAGO', 'Pago'
    PARCIALMENTE_PAGO = 'PARCIALMENTE_PAGO', 'Parcialmente Pago'
    ATRASADO = 'ATRASADO', 'Atrasado'
    CANCELADO = 'CANCELADO', 'Cancelado'

class PaymentMethodChoices(models.TextChoices):
    PIX = 'PIX', 'Pix'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferência Bancária (TED/DOC)'
    BOLETO = 'BOLETO', 'Boleto Bancário'
    CARTAO = 'CARTAO', 'Cartão de Crédito/Débito'
    DINHEIRO = 'DINHEIRO', 'Dinheiro'


class PayableBill(models.Model):
    supplier = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='payable_bills', verbose_name='Fornecedor / Favorecido')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='payable_bills', verbose_name='Projeto (Apropriação de Custo)')
    
    bill_number = models.CharField('Número do Documento / NF / Boleto', max_length=50)
    category = models.CharField('Categoria da Despesa', max_length=50, choices=BillCategoryChoices.choices, default=BillCategoryChoices.MATERIAIS_OBRA)
    
    issue_date = models.DateField('Data de Emissão', default=timezone.now)
    due_date = models.DateField('Data de Vencimento')
    
    amount = models.DecimalField('Valor a Pagar (R$)', max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField('Valor Pago (R$)', max_digits=12, decimal_places=2, default=0.00)
    
    status = models.CharField('Status do Pagamento', max_length=50, choices=BillStatusChoices.choices, default=BillStatusChoices.EM_ABERTO)
    
    bill_file = models.FileField('Anexo da Conta (PDF / Imagem)', upload_to='payables/bills/%Y/%m/', null=True, blank=True)
    notes = models.TextField('Observações / Histórico de Compliance', blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_payable_bills', verbose_name='Cadastrado por')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'

    def __str__(self):
        return f"{self.bill_number} - {self.supplier.name} (R$ {self.amount})"

    @property
    def is_overdue(self):
        """Verifica se a conta está vencida e não quitada."""
        if self.status in [BillStatusChoices.EM_ABERTO, BillStatusChoices.PARCIALMENTE_PAGO] and self.due_date:
            return self.due_date < timezone.now().date()
        return False

    @property
    def is_due_soon(self):
        """Verifica se a conta vence nos próximos 7 dias."""
        if self.status in [BillStatusChoices.EM_ABERTO, BillStatusChoices.PARCIALMENTE_PAGO] and self.due_date:
            today = timezone.now().date()
            return today <= self.due_date <= (today + timedelta(days=7))
        return False

    @property
    def remaining_amount(self):
        """Calcula o valor restante a pagar."""
        return max(Decimal('0.00'), self.amount - self.amount_paid)


class PaymentReceipt(models.Model):
    bill = models.ForeignKey(PayableBill, on_delete=models.CASCADE, related_name='receipts', verbose_name='Conta a Pagar')
    payment_date = models.DateField('Data do Efetivo Pagamento', default=timezone.now)
    amount_paid = models.DecimalField('Valor Pago nesta Transação (R$)', max_digits=12, decimal_places=2)
    payment_method = models.CharField('Forma de Pagamento', max_length=50, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.PIX)
    
    receipt_file = models.FileField('Comprovante / Recibo (PDF / Imagem)', upload_to='payables/receipts/%Y/%m/', null=True, blank=True)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Registrado por')
    notes = models.TextField('Observações do Pagamento', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Comprovante de Pagamento'
        verbose_name_plural = 'Comprovantes de Pagamento'

    def __str__(self):
        return f"Comprovante R$ {self.amount_paid} ({self.payment_date}) - {self.bill.bill_number}"
