import hashlib
from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.contacts.models import Contact, ContactTypeChoices
from apps.commercial.models import (
    CommercialProposal,
    ProposalScopeItem,
    ProposalInputRequirement,
    LegalContract,
    ProposalStatusChoices,
    ContractStatusChoices,
    InputStatusChoices,
    InputItemTypeChoices,
    ServiceTypeChoices,
    ContractTypeChoices,
    generate_proposal_code
)
from apps.audit_log.models import AuditLog, AuditActionChoices

User = get_user_model()

class CommercialModuleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email='comercial.admin@pangea.eng.br',
            password='Password#2026',
            first_name='Carlos',
            last_name='Silva'
        )
        self.client_auth = Client()
        self.client_auth.force_login(self.user)
        self.client_anon = Client()

        self.contact = Contact.objects.create(
            name='Construtora Manaus Obras Ltda',
            contact_type=ContactTypeChoices.COMPANY,
            doc_number='11222333000181',
            city='Manaus',
            state='AM'
        )

    # 1. RF-01: Cadastro, Codificação e Parametrização da Proposta
    def test_proposal_creation_code_and_default_inputs(self):
        code = generate_proposal_code(2026)
        self.assertTrue(code.startswith("PROP-"))
        self.assertTrue(code.endswith("A/2026"))

        # Criação via view
        res = self.client_auth.post('/commercial/proposals/create/', {
            'client': str(self.contact.pk),
            'project_name': 'Edifício Encosta do Rio Negro',
            'project_location': 'Ponta Negra, Manaus/AM',
            'salesperson': str(self.user.pk),
            'technical_responsible': str(self.user.pk),
            'validity_days': 30,
            'execution_lead_time_days': 25,
            'total_value': '0.00',
            'payment_terms_desc': '50% entrada e 50% na entrega.'
        })
        self.assertEqual(res.status_code, 302)

        proposal = CommercialProposal.objects.get(project_name='Edifício Encosta do Rio Negro')
        self.assertEqual(proposal.validity_days, 30)
        self.assertEqual(proposal.execution_lead_time_days, 25)
        
        # Verifica seed automático dos 3 insumos mandatórios da Pangea
        inputs = proposal.input_requirements.all()
        self.assertEqual(inputs.count(), 3)
        self.assertTrue(inputs.filter(required_item_type=InputItemTypeChoices.SONDAGEM_SPT).exists())
        self.assertTrue(inputs.filter(required_item_type=InputItemTypeChoices.PLANTA_CARGAS).exists())
        self.assertTrue(inputs.filter(required_item_type=InputItemTypeChoices.ARQUITETURA_DWG).exists())

    # 2. RF-01: Itens de Escopo e Imutabilidade
    def test_scope_items_and_immutability_on_acceptance(self):
        proposal = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Contenção Muro de Flexão',
            salesperson=self.user,
            technical_responsible=self.user,
            validity_days=30
        )

        # Adiciona Item 1: Fundações
        item1 = ProposalScopeItem.objects.create(
            proposal=proposal,
            service_type=ServiceTypeChoices.FUNDACOES,
            nbr_references='NBR 6122 / NBR 6118',
            description='Dimensionamento de sapatas e estacas.',
            subtotal_value=Decimal('25000.00')
        )

        # Adiciona Item 2: Contenções
        item2 = ProposalScopeItem.objects.create(
            proposal=proposal,
            service_type=ServiceTypeChoices.CONTENCOES,
            nbr_references='NBR 11682',
            description='Cortina de contenção atirantada.',
            subtotal_value=Decimal('35000.00')
        )

        proposal.refresh_from_db()
        self.assertEqual(proposal.total_value, Decimal('60000.00'))

        # Aceita a proposta
        proposal.accept_online(
            signer_name='Dr. Roberto Fagundes',
            signer_doc='12345678909',
            signer_role='Diretor',
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0'
        )
        self.assertEqual(proposal.status, ProposalStatusChoices.ACEITA)

        # Tentar alterar valor após aceite deve lançar ValidationError
        proposal.total_value = Decimal('99000.00')
        with self.assertRaises(ValidationError):
            proposal.clean()

    # 3. RF-02: Portal Público e Aceite Eletrônico Legal
    def test_public_portal_and_online_acceptance(self):
        proposal = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Ponte sobre o Igarapé',
            salesperson=self.user,
            technical_responsible=self.user,
            total_value=Decimal('45000.00'),
            validity_days=15
        )

        # Acesso anônimo via token público na Landing Page
        url_portal = f'/commercial/public/proposal/{proposal.public_token}/'
        res_portal = self.client_anon.get(url_portal)
        self.assertEqual(res_portal.status_code, 200)
        self.assertContains(res_portal, proposal.proposal_code)
        self.assertContains(res_portal, 'Pangea Engenharia Ltda.')

        # Submissão de Aceite Eletrônico
        url_action = f'/commercial/public/proposal/{proposal.public_token}/action/'
        res_accept = self.client_anon.post(url_action, {
            'action': 'accept',
            'signer_name': 'Carlos Eduardo Meireles',
            'signer_doc': '99887766000155',
            'signer_role': 'Sócio Administrador',
            'confirm_terms': 'on'
        }, follow=True)
        self.assertEqual(res_accept.status_code, 200)

        proposal.refresh_from_db()
        self.assertEqual(proposal.status, ProposalStatusChoices.ACEITA)
        self.assertEqual(proposal.acceptance_signer_name, 'Carlos Eduardo Meireles')
        self.assertIsNotNone(proposal.accepted_at)
        self.assertTrue(len(proposal.acceptance_hash) == 64) # SHA-256

        # Minuta contratual instanciada automaticamente
        self.assertTrue(hasattr(proposal, 'contract'))
        contract = proposal.contract
        self.assertEqual(contract.contract_code, proposal.proposal_code.replace("PROP-", "CTR-"))
        self.assertEqual(contract.status, ContractStatusChoices.MINUTA)
        self.assertIn('PANGEA ENGENHARIA LTDA', contract.contract_html_body)
        self.assertIn('Manaus', contract.contract_html_body)

    # 4. RF-02: Bloqueio de Aceite em Proposta Expirada
    def test_expired_proposal_blocks_acceptance(self):
        proposal = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Galpão Logístico Distrito',
            salesperson=self.user,
            validity_days=15,
            expires_at=date.today() - timedelta(days=2) # Expirou há 2 dias
        )
        self.assertTrue(proposal.is_expired())

        with self.assertRaises(ValidationError):
            proposal.accept_online(
                signer_name='Cliente Atrasado',
                signer_doc='12345678909',
                signer_role='Gerente',
                ip_address='127.0.0.1',
                user_agent='TestAgent'
            )

    # 5. RF-02: Solicitação de Revisão e Recusa
    def test_client_revision_and_rejection(self):
        proposal = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Edifício Mirante',
            salesperson=self.user,
            validity_days=30
        )
        url_action = f'/commercial/public/proposal/{proposal.public_token}/action/'

        # 5.1 Solicita revisão
        res_rev = self.client_anon.post(url_action, {
            'action': 'revision',
            'revision_notes': 'Favor incluir laudo de sondagem CPTu no escopo.'
        }, follow=True)
        self.assertEqual(res_rev.status_code, 200)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, ProposalStatusChoices.EM_REVISAO)
        self.assertIn('CPTu', proposal.revision_notes)

        # 5.2 Recusa da proposta
        res_rej = self.client_anon.post(url_action, {
            'action': 'reject',
            'rejection_reason': 'Projeto cancelado pela diretoria do cliente.'
        }, follow=True)
        self.assertEqual(res_rej.status_code, 200)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, ProposalStatusChoices.DECLINADA)

    # 6. RF-04: Homologação de Insumos e Gatilho de Mise en Service
    def test_mise_en_service_governance_trigger(self):
        proposal = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Complexo Portuário Chibatão',
            salesperson=self.user,
            technical_responsible=self.user,
            execution_lead_time_days=20,
            validity_days=30
        )
        # Insumo obrigatório
        spt_req = ProposalInputRequirement.objects.create(
            proposal=proposal,
            required_item_type=InputItemTypeChoices.SONDAGEM_SPT,
            is_mandatory=True
        )

        contract = proposal.create_contract_draft()
        self.assertEqual(contract.status, ContractStatusChoices.MINUTA)

        # Tentativa 1: Acionar sem contrato assinado, sem insumos e sem ART -> Deve falhar
        can_start, pendencias = contract.can_trigger_mise_en_service()
        self.assertFalse(can_start)
        self.assertEqual(len(pendencias), 3)

        with self.assertRaises(ValidationError):
            contract.trigger_mise_en_service(self.user)

        # Passo A: Anexa contrato assinado
        fake_contract_pdf = SimpleUploadedFile("contrato_assinado.pdf", b"%PDF-1.4...", content_type="application/pdf")
        contract.signed_pdf = fake_contract_pdf
        contract.signed_at = date.today()
        contract.status = ContractStatusChoices.ASSINADO
        contract.save()

        # Passo B: Registra ART no CREA-AM
        contract.crea_art_number = "ART-CREA-AM-2026-998811"
        contract.save()

        # Passo C: Engenheiro Geotécnico valida os furos de sondagem SPT
        spt_req.approve_input(self.user, notes="Laudo SPT com 5 furos aprovado conforme NBR 6484.")
        self.assertEqual(spt_req.status, InputStatusChoices.APROVADO)

        # Agora todas as 3 pré-condições estão satisfeitas!
        can_start, pendencias = contract.can_trigger_mise_en_service()
        self.assertTrue(can_start)
        self.assertEqual(len(pendencias), 0)

        # Dispara o Mise en Service (D0)
        d0, deadline = contract.trigger_mise_en_service(self.user)
        self.assertEqual(d0, timezone.now().date())
        self.assertEqual(deadline, d0 + timedelta(days=20))
        self.assertEqual(contract.status, ContractStatusChoices.MISE_EN_SERVICE)

    # 7. Auditoria Imutável das Operações Comerciais
    def test_commercial_audit_logging(self):
        initial_logs = AuditLog.objects.filter(app_label='commercial').count()

        prop = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Auditoria Obra Teste',
            salesperson=self.user,
            total_value=Decimal('10000.00')
        )

        logs_prop = AuditLog.objects.filter(model_name='commercialproposal', object_id=str(prop.pk))
        self.assertTrue(logs_prop.filter(action=AuditActionChoices.CREATE).exists())
