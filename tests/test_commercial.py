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
    generate_proposal_code,
    TechnicalDiscipline,
    TechnicalServiceType,
    TechnicalInputType
)
from apps.commercial.templatetags.currency_filters import currency_br, number_br, parse_decimal_br
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

    # 8. Modificação/Edição de Itens de Escopo Técnico Parametrizado
    def test_edit_scope_item_and_total_recalculation(self):
        proposal = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Edifício Mirante da Colina',
            salesperson=self.user,
            validity_days=30
        )

        # Adiciona item inicial: R$ 20.000,00
        item = ProposalScopeItem.objects.create(
            proposal=proposal,
            service_type='Dimensionamento de Fundações',
            nbr_references='NBR 6122',
            description='Fundações em estacas cravadas',
            subtotal_value=Decimal('20000.00')
        )
        proposal.refresh_from_db()
        self.assertEqual(proposal.total_value, Decimal('20000.00'))

        # GET no modal de edição
        url_edit = f'/commercial/proposals/{proposal.pk}/scope/{item.pk}/edit/'
        res_get = self.client_auth.get(url_edit)
        self.assertEqual(res_get.status_code, 200)
        self.assertContains(res_get, 'Modificar Item de Escopo Técnico')
        self.assertContains(res_get, '20.000,00')

        # POST modificando valores e textos (passando valor em padrão brasileiro 35.500,50)
        res_post = self.client_auth.post(url_edit, {
            'discipline_name': 'Fundações e Geotecnia',
            'service_type_name': 'Dimensionamento de Fundações Superficiais e Profundas (NBR 6122 / NBR 6118)',
            'nbr_references': 'ABNT NBR 6122:2019 e NBR 6118:2023',
            'description': 'Dimensionamento atualizado para estacas hélice contínua',
            'subtotal_value': '35.500,50'
        })
        self.assertEqual(res_post.status_code, 302)

        # Verifica recálculo automático do total da proposta
        item.refresh_from_db()
        proposal.refresh_from_db()
        self.assertEqual(item.subtotal_value, Decimal('35500.50'))
        self.assertEqual(proposal.total_value, Decimal('35500.50'))
        self.assertEqual(item.nbr_references, 'ABNT NBR 6122:2019 e NBR 6118:2023')

    def test_cannot_edit_scope_item_when_proposal_accepted(self):
        proposal = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Galpão Logístico Tarumã',
            salesperson=self.user,
            validity_days=30
        )
        item = ProposalScopeItem.objects.create(
            proposal=proposal,
            service_type='Contenções de Divisa',
            subtotal_value=Decimal('15000.00')
        )
        # Agora aceita a proposta
        proposal.status = ProposalStatusChoices.ACEITA
        proposal.save(update_fields=['status'])

        url_edit = f'/commercial/proposals/{proposal.pk}/scope/{item.pk}/edit/'
        # GET deve redirecionar com mensagem de erro
        res_get = self.client_auth.get(url_edit)
        self.assertEqual(res_get.status_code, 302)

        # POST também não deve permitir alteração
        res_post = self.client_auth.post(url_edit, {
            'service_type_name': 'Novo Serviço',
            'subtotal_value': '50.000,00'
        })
        self.assertEqual(res_post.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.subtotal_value, Decimal('15000.00'))

    # 9. Criação Dinâmica Inline de Disciplina e Tipo de Serviço
    def test_dynamic_discipline_and_service_type_inline_creation(self):
        proposal = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Ensaio de Placa In Situ',
            salesperson=self.user,
            validity_days=15
        )

        nova_disciplina = 'Geofísica e Ensaios Especiais'
        novo_servico = 'Ensaio de Prova de Carga Estática sobre Placa (NBR 6489)'

        self.assertFalse(TechnicalDiscipline.objects.filter(name=nova_disciplina).exists())
        self.assertFalse(TechnicalServiceType.objects.filter(name=novo_servico).exists())

        # Envia formulário adicionando item com disciplina e serviço inéditos
        url_add = f'/commercial/proposals/{proposal.pk}/scope/add/'
        res = self.client_auth.post(url_add, {
            'discipline_name': nova_disciplina,
            'service_type_name': novo_servico,
            'nbr_references': 'ABNT NBR 6489:2019',
            'description': 'Execução de ensaios com placa de reação e extensômetros digitais',
            'subtotal_value': '18.750,00'
        })
        self.assertEqual(res.status_code, 302)

        # Confirma que a nova Disciplina e o novo Tipo de Serviço foram persistidos no banco
        disc = TechnicalDiscipline.objects.filter(name=nova_disciplina).first()
        self.assertIsNotNone(disc)
        self.assertTrue(disc.is_active)

        serv = TechnicalServiceType.objects.filter(name=novo_servico).first()
        self.assertIsNotNone(serv)
        self.assertEqual(serv.discipline, disc)
        self.assertEqual(serv.default_nbr_references, 'ABNT NBR 6489:2019')

        # Confirma item da proposta vinculado
        item = proposal.scope_items.first()
        self.assertEqual(item.discipline, disc)
        self.assertEqual(item.service_type_ref, serv)
        self.assertEqual(item.subtotal_value, Decimal('18750.00'))
    # 10. Criação Dinâmica Inline de Tipo de Insumo
    def test_dynamic_input_type_inline_creation(self):
        proposal = CommercialProposal.objects.create(
            client=self.contact,
            project_name='Píer Fluvial Rio Negro',
            salesperson=self.user,
            validity_days=30
        )

        novo_insumo = 'Batimetria e Perfil Sísmico Contínuo'
        self.assertFalse(TechnicalInputType.objects.filter(name=novo_insumo).exists())

        url_add_inp = f'/commercial/proposals/{proposal.pk}/inputs/add/'
        res = self.client_auth.post(url_add_inp, {
            'input_type_name': novo_insumo,
            'description': 'Levantamento batimétrico multifeixe com amarração geodésica',
            'is_mandatory': True
        })
        self.assertEqual(res.status_code, 302)
        # Confirma persistência do novo Tipo de Insumo no banco
        inp_type = TechnicalInputType.objects.filter(name=novo_insumo).first()
        self.assertIsNotNone(inp_type)
        self.assertTrue(inp_type.is_active)

        # Confirma insumo cadastrado na proposta
        req = proposal.input_requirements.filter(input_type_ref=inp_type).first()
        self.assertIsNotNone(req)
        self.assertTrue(req.is_mandatory)

    # 11. Formatação e Parsing de Valores Monetários em R$ (Padrão Brasileiro)
    def test_brazilian_currency_formatting_and_parsing(self):
        # Testes de template filter
        self.assertEqual(currency_br(Decimal('42000.00')), 'R$ 42.000,00')
        self.assertEqual(currency_br(Decimal('1234.56')), 'R$ 1.234,56')
        self.assertEqual(currency_br(Decimal('1500000.00')), 'R$ 1.500.000,00')
        self.assertEqual(currency_br(Decimal('0.00')), 'R$ 0,00')
        self.assertEqual(currency_br(None), 'R$ 0,00')

        self.assertEqual(number_br(Decimal('42000.00')), '42.000,00')
        self.assertEqual(number_br(Decimal('1234.56')), '1.234,56')

        # Testes de parsing tolerante
        self.assertEqual(parse_decimal_br('42.000,00'), Decimal('42000.00'))
        self.assertEqual(parse_decimal_br('42000,00'), Decimal('42000.00'))
        self.assertEqual(parse_decimal_br('42000.00'), Decimal('42000.00'))
        self.assertEqual(parse_decimal_br('R$ 1.234,56'), Decimal('1234.56'))
        self.assertEqual(parse_decimal_br(''), Decimal('0.00'))
