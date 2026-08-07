from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from contacts.models import Contact
from .models import Lead, Proposal, Contract, ServiceTypeChoices, ProposalStatusChoices

User = get_user_model()

class CommercialTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='engineer', password='password123')
        self.client.login(username='engineer', password='password123')
        self.contact = Contact.objects.create(name='Construtora Teste Ltda', person_type='PJ')

    def test_lead_creation(self):
        response = self.client.post(reverse('lead_create'), {
            'contact': self.contact.pk,
            'source': 'Site',
            'service_of_interest': ServiceTypeChoices.FUNDACOES,
            'description': 'Projeto de fundação profunda para edifício de 15 andares.',
            'estimated_value': 150000.00,
            'probability': 70,
            'stage': 'NOVO',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lead.objects.filter(contact=self.contact).exists())

    def test_proposal_historical_versioning(self):
        # Create initial proposal v1
        proposal_v1 = Proposal.objects.create(
            number='PROP-2026-999',
            version=1,
            client=self.contact,
            scope='Escopo inicial v1',
            total_value=50000.00,
            status=ProposalStatusChoices.RASCUNHO
        )

        # Trigger create new version (Requisito 573)
        response = self.client.get(reverse('proposal_create_new_version', args=[proposal_v1.pk]))
        self.assertEqual(response.status_code, 302)

        # Verify proposal v2 exists and v1 is preserved
        self.assertTrue(Proposal.objects.filter(number='PROP-2026-999', version=1).exists())
        self.assertTrue(Proposal.objects.filter(number='PROP-2026-999', version=2).exists())
        
        proposal_v2 = Proposal.objects.get(number='PROP-2026-999', version=2)
        self.assertEqual(proposal_v2.parent_proposal, proposal_v1)

    def test_contract_creation(self):
        proposal = Proposal.objects.create(
            number='PROP-2026-888',
            version=1,
            client=self.contact,
            scope='Escopo aprovado',
            total_value=80000.00,
            status=ProposalStatusChoices.APROVADA
        )

        response = self.client.post(reverse('contract_create'), {
            'number': 'CONT-2026-888',
            'client': self.contact.pk,
            'proposal': proposal.pk,
            'start_date': '2026-08-01',
            'total_value': 80000.00,
            'readjustment_index': 'IPCA',
            'status': 'ATIVO',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Contract.objects.filter(number='CONT-2026-888').exists())
