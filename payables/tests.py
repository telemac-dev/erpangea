from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import CustomUser, UserRoleChoices
from contacts.models import Contact
from .models import PayableBill, PaymentReceipt, BillStatusChoices, BillCategoryChoices

class PayablesTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='fin_manager', password='password123', role=UserRoleChoices.MANAGER
        )
        self.client.login(username='fin_manager', password='password123')
        self.supplier = Contact.objects.create(name='Fornecedor de Concreto Ltda', person_type='PJ')

    def test_bill_creation_and_due_soon(self):
        today = date.today()
        dummy_file = SimpleUploadedFile("nota.pdf", b"pdf content", content_type="application/pdf")
        
        bill = PayableBill.objects.create(
            supplier=self.supplier,
            bill_number='NF-888',
            category=BillCategoryChoices.MATERIAIS_OBRA,
            issue_date=today - timedelta(days=5),
            due_date=today + timedelta(days=3), # Due in 3 days
            amount=25000.00,
            status=BillStatusChoices.EM_ABERTO,
            bill_file=dummy_file
        )

        self.assertTrue(bill.is_due_soon)
        self.assertFalse(bill.is_overdue)

    def test_register_payment_and_receipt_attachment(self):
        today = date.today()
        bill = PayableBill.objects.create(
            supplier=self.supplier,
            bill_number='NF-999',
            category=BillCategoryChoices.EQUIPAMENTOS,
            issue_date=today - timedelta(days=10),
            due_date=today + timedelta(days=10),
            amount=10000.00,
            status=BillStatusChoices.EM_ABERTO
        )

        receipt_file = SimpleUploadedFile("comprovante.pdf", b"receipt content", content_type="application/pdf")
        response = self.client.post(reverse('bill_detail', args=[bill.pk]), {
            'payment_date': '2026-08-05',
            'amount_paid': 10000.00,
            'payment_method': 'PIX',
            'receipt_file': receipt_file,
            'notes': 'Pagamento via PIX realizado com sucesso'
        })
        self.assertEqual(response.status_code, 302)

        bill.refresh_from_db()
        self.assertEqual(bill.status, BillStatusChoices.PAGO)
        self.assertEqual(bill.amount_paid, 10000.00)
        self.assertTrue(PaymentReceipt.objects.filter(bill=bill).exists())

    def test_payables_report_access(self):
        response = self.client.get(reverse('payables_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatório Consolidado de Contas a Pagar')
