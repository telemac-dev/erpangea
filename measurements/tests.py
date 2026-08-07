from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from projects.models import Project
from contacts.models import Contact
from .models import Measurement, MeasurementStatusChoices

User = get_user_model()

class MeasurementsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='engineer', password='password123')
        self.client.login(username='engineer', password='password123')
        self.contact = Contact.objects.create(name='Cliente Construtora Medição', person_type='PJ')
        self.project = Project.objects.create(
            code='PRJ-MED-001',
            name='Projeto de Sondagem e Fundação',
            client=self.contact,
            start_date=date.today(),
            expected_completion_date=date.today() + timedelta(days=30)
        )

    def test_measurement_creation(self):
        response = self.client.post(reverse('measurement_create'), {
            'project': self.project.pk,
            'number': 'MED-2026-999',
            'measurement_date': '2026-08-05',
            'period_start': '2026-08-01',
            'period_end': '2026-08-05',
            'measured_value': 65000.00,
            'percentage_completed': 50.00,
            'description': 'Medição de 50% das estacas perfuradas',
            'status': MeasurementStatusChoices.EM_ELABORACAO
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Measurement.objects.filter(number='MED-2026-999').exists())

    def test_measurement_approval_action(self):
        measurement = Measurement.objects.create(
            project=self.project,
            number='MED-2026-888',
            measurement_date=date.today(),
            period_start=date.today(),
            period_end=date.today(),
            measured_value=30000.00,
            description='Medição inicial de laudo geotécnico',
            status=MeasurementStatusChoices.AGUARDANDO_APROVACAO
        )

        response = self.client.post(reverse('measurement_approve', args=[measurement.pk]))
        self.assertEqual(response.status_code, 302)

        measurement.refresh_from_db()
        self.assertEqual(measurement.status, MeasurementStatusChoices.APROVADA)
        self.assertEqual(measurement.approved_by, self.user)
        self.assertIsNotNone(measurement.approval_date)
