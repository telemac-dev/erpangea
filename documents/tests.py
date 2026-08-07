from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from projects.models import Project
from contacts.models import Contact
from .models import Document, DocumentRevision, DocumentCategoryChoices, DocumentStatusChoices

User = get_user_model()

class DocumentsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='engineer', password='password123')
        self.client.login(username='engineer', password='password123')
        self.contact = Contact.objects.create(name='Cliente Construtora', person_type='PJ')
        self.project = Project.objects.create(
            code='PRJ-DOC-001',
            name='Projeto Geotécnico',
            client=self.contact,
            start_date='2026-08-01',
            expected_completion_date='2026-09-01'
        )

    def test_document_creation(self):
        dummy_file = SimpleUploadedFile("memorial.pdf", b"pdf content", content_type="application/pdf")
        response = self.client.post(reverse('document_create'), {
            'project': self.project.pk,
            'title': 'Memorial de Cálculo de Fundação',
            'category': DocumentCategoryChoices.MEMORIAL_CALCULO,
            'file': dummy_file,
            'revision': 'R00',
            'status': DocumentStatusChoices.EM_ELABORACAO,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Document.objects.filter(title='Memorial de Cálculo de Fundação').exists())

    def test_document_new_revision_submission(self):
        dummy_file_1 = SimpleUploadedFile("prancha_r00.dwg", b"dwg r00 content", content_type="application/octet-stream")
        doc = Document.objects.create(
            project=self.project,
            title='Prancha de Armação de Pilar',
            category=DocumentCategoryChoices.DESENHO_CAD,
            file=dummy_file_1,
            revision='R00',
            status=DocumentStatusChoices.EM_ELABORACAO
        )

        dummy_file_2 = SimpleUploadedFile("prancha_r01.dwg", b"dwg r01 content", content_type="application/octet-stream")
        response = self.client.post(reverse('document_detail', args=[doc.pk]), {
            'revision_number': 'R01',
            'file': dummy_file_2,
            'changes_summary': 'Revisão das armaduras do pilar P1 e P2 conforme cálculo geotécnico.'
        })
        self.assertEqual(response.status_code, 302)

        doc.refresh_from_db()
        self.assertEqual(doc.revision, 'R01')
        self.assertEqual(doc.status, DocumentStatusChoices.EM_REVISAO)
        self.assertTrue(DocumentRevision.objects.filter(document=doc, revision_number='R01').exists())
