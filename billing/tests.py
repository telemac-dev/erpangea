from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser, UserRoleChoices
from contacts.models import Contact
from .models import Invoice, InvoiceStatusChoices

class BillingTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='engineer', password='password123', role=UserRoleChoices.ADMINISTRATOR
        )
        self.client.login(username='engineer', password='password123')
        self.contact = Contact.objects.create(name='Cliente Construtora Faturamento', person_type='PJ')

    def test_invoice_creation_and_overdue_property(self):
        today = date.today()
        inv = Invoice.objects.create(
            invoice_number='NF-TEST-001',
            client=self.contact,
            issue_date=today - timedelta(days=40),
            due_date=today - timedelta(days=10),
            amount=50000.00,
            status=InvoiceStatusChoices.EM_ABERTO
        )
        self.assertTrue(inv.is_overdue)

    def test_invoice_register_payment_action(self):
        inv = Invoice.objects.create(
            invoice_number='NF-TEST-002',
            client=self.contact,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            amount=80000.00,
            status=InvoiceStatusChoices.EM_ABERTO
        )

        response = self.client.post(reverse('invoice_register_payment', args=[inv.pk]))
        self.assertEqual(response.status_code, 302)

        inv.refresh_from_db()
        self.assertEqual(inv.status, InvoiceStatusChoices.PAGO)
        self.assertEqual(inv.amount_paid, 80000.00)
        self.assertIsNotNone(inv.payment_date)
