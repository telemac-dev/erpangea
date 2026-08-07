from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from contacts.models import Contact
from .models import Project, Task, Delivery, ProjectStatusChoices, TaskStatusChoices

User = get_user_model()

class ProjectsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='engineer', password='password123')
        self.client.login(username='engineer', password='password123')
        self.contact = Contact.objects.create(name='Construtora Horizonte', person_type='PJ')

    def test_project_creation_and_delayed_property(self):
        today = date.today()
        project = Project.objects.create(
            code='PRJ-TEST-001',
            name='Projeto de Fundação Teste',
            client=self.contact,
            start_date=today - timedelta(days=30),
            expected_completion_date=today - timedelta(days=5),
            status=ProjectStatusChoices.EM_ANDAMENTO
        )
        self.assertTrue(project.is_delayed)

    def test_task_creation_and_status_update(self):
        project = Project.objects.create(
            code='PRJ-TEST-002',
            name='Projeto Geotécnico',
            client=self.contact,
            start_date=date.today(),
            expected_completion_date=date.today() + timedelta(days=30),
        )
        
        task = Task.objects.create(
            project=project,
            name='Ensaio de SPT',
            assigned_to=self.user,
            status=TaskStatusChoices.PENDENTE
        )

        response = self.client.post(reverse('task_update_status', args=[task.pk]), {
            'status': TaskStatusChoices.CONCLUIDA
        })
        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.status, TaskStatusChoices.CONCLUIDA)

    def test_add_delivery_to_project(self):
        project = Project.objects.create(
            code='PRJ-TEST-003',
            name='Projeto de Contenção',
            client=self.contact,
            start_date=date.today(),
            expected_completion_date=date.today() + timedelta(days=30),
        )

        response = self.client.post(reverse('project_detail', args=[project.pk]), {
            'action_delivery': '1',
            'title': 'Entrega R00 - Relatório Geotécnico',
            'description': 'Cálculos e pranchas enviadas ao cliente',
            'delivery_date': '2026-08-05',
            'status': 'AGUARDANDO_APROVACAO',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Delivery.objects.filter(project=project, title='Entrega R00 - Relatório Geotécnico').exists())
