from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from datetime import date, timedelta

from core_auth.models import User, UserProfile, SectorEnum
from contacts.models import Contact, PersonTypeEnum
from commercial.models import Proposal, Contract, WorkOrder, ProposalStatusEnum, DisciplineEnum, BillingModeEnum, OSStatusEnum
from projects.models import Project, ProjectPhase, Task, TaskStatusEnum, ProjectStatusEnum
from edms_docs.models import ProjectDocument, DocumentRevision, DocumentTypeEnum, RevisionStatusEnum
from measurements.models import MeasurementSheet, MeasurementStatusEnum
from invoices.models import ServiceInvoice, AccountReceivable, InvoiceStatusEnum
from financial.models import AccountPayable, PayableStatusEnum, CostCenterEnum
from audit_log.models import ActivityLog

class ERPangeaFullSuiteTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email='testadmin@pangea.com', password='password123')
        self.tech_user = User.objects.create_user(email='tech@pangea.com', password='password123')
        UserProfile.objects.create(user=self.tech_user, setor=SectorEnum.TECNICO)
        
        self.client = Client()
        self.client.force_login(self.user)

        self.contact = Contact.objects.create(
            tipo_pessoa=PersonTypeEnum.PJ,
            razao_social_nome='Infraestrutura Nacional Ltda',
            cpf_cnpj='99887766000155',
            classificacoes=['CLIENTE']
        )

    # 1. TESTES DO MÓDULO COMERCIAL
    def test_proposal_scope_lock_on_approval(self):
        prop = Proposal.objects.create(
            cliente=self.contact,
            disciplina_principal=DisciplineEnum.CONTENCOES,
            valor_global=Decimal('80000.00'),
            validade=date.today() + timedelta(days=30),
            status=ProposalStatusEnum.RASCUNHO
        )
        self.assertTrue(prop.codigo_proposta.startswith("PROP-"))
        
        # Aprova a proposta
        prop.status = ProposalStatusEnum.APROVADA
        prop.save()
        
        # Verifica se gerou minuta de contrato automaticamente via signal
        self.assertTrue(hasattr(prop, 'contract'))
        self.assertEqual(prop.contract.valor_total_contratado, Decimal('80000.00'))

        # Tentar alterar valor de proposta aprovada deve falhar
        prop.valor_global = Decimal('95000.00')
        with self.assertRaises(ValidationError):
            prop.save()

    def test_work_order_activation_requires_signed_contract(self):
        prop = Proposal.objects.create(
            cliente=self.contact,
            disciplina_principal=DisciplineEnum.FUNDACOES,
            valor_global=Decimal('50000.00'),
            validade=date.today(),
            status=ProposalStatusEnum.APROVADA
        )
        contract = prop.contract
        
        # Tenta ativar a OS sem contrato assinado
        wo = WorkOrder(
            contrato=contract,
            coordenador_tecnico=self.tech_user,
            status=OSStatusEnum.ATIVA
        )
        with self.assertRaises(ValidationError):
            wo.full_clean()
            wo.save()

        # Anexa PDF assinado no contrato
        fake_pdf = SimpleUploadedFile("contrato_assinado.pdf", b"%PDF-1.4...", content_type="application/pdf")
        contract.documento_assinado = fake_pdf
        contract.save()

        # Agora a OS pode ser ativada
        wo.status = OSStatusEnum.ATIVA
        wo.full_clean()
        wo.save()
        self.assertEqual(wo.status, OSStatusEnum.ATIVA)

    # 2. TESTES DE PROJETOS E EDMS
    def test_project_delivery_requires_approved_art(self):
        prop = Proposal.objects.create(
            cliente=self.contact,
            disciplina_principal=DisciplineEnum.ESTRUTURAS,
            valor_global=Decimal('40000.00'),
            validade=date.today(),
            status=ProposalStatusEnum.APROVADA
        )
        contract = prop.contract
        contract.documento_assinado = SimpleUploadedFile("c.pdf", b"%PDF...", content_type="application/pdf")
        contract.save()
        
        wo = WorkOrder.objects.create(contrato=contract, coordenador_tecnico=self.tech_user, status=OSStatusEnum.ATIVA)
        project = Project.objects.create(ordem_servico=wo, nome_projeto='Edifício Horizonte')

        # Tentar entregar o projeto sem ART aprovada deve falhar
        project.status = ProjectStatusEnum.ENTREGUE
        with self.assertRaises(ValidationError):
            project.full_clean()
            project.save()

        # Cria ART e aprova
        art_doc = ProjectDocument.objects.create(
            projeto=project,
            tipo=DocumentTypeEnum.ART_CREA,
            codigo_identificador='ART-HORIZONTE-01',
            titulo='ART Execução'
        )
        art_rev = DocumentRevision.objects.create(
            documento=art_doc,
            arquivo=SimpleUploadedFile("art.pdf", b"%PDF...", content_type="application/pdf"),
            enviado_por=self.user,
            status=RevisionStatusEnum.APROVADO_CLIENTE
        )

        # Agora o projeto pode ser entregue
        project.status = ProjectStatusEnum.ENTREGUE
        project.full_clean()
        project.save()
        self.assertEqual(project.status, ProjectStatusEnum.ENTREGUE)

    def test_edms_revision_auto_increment(self):
        prop = Proposal.objects.create(cliente=self.contact, disciplina_principal=DisciplineEnum.CONSULTORIA, valor_global=Decimal('10000.00'), validade=date.today(), status=ProposalStatusEnum.APROVADA)
        wo = WorkOrder.objects.create(contrato=prop.contract, coordenador_tecnico=self.tech_user, status=OSStatusEnum.PLANEJAMENTO)
        project = Project.objects.create(ordem_servico=wo, nome_projeto='Estudo de Talude')

        doc = ProjectDocument.objects.create(projeto=project, tipo=DocumentTypeEnum.RELATORIO_TECNICO, codigo_identificador='REL-01', titulo='Relatório Geotécnico')
        
        rev0 = DocumentRevision.objects.create(documento=doc, arquivo=SimpleUploadedFile("r0.pdf", b"%PDF...", content_type="application/pdf"), enviado_por=self.user)
        self.assertEqual(rev0.revisao, 'R00')

        rev1 = DocumentRevision.objects.create(documento=doc, arquivo=SimpleUploadedFile("r1.pdf", b"%PDF...", content_type="application/pdf"), enviado_por=self.user)
        self.assertEqual(rev1.revisao, 'R01')

    # 3. TESTES DE MEDIÇÕES E FATURAMENTO
    def test_measurement_ceiling_and_nfs_e_receivables(self):
        prop = Proposal.objects.create(cliente=self.contact, disciplina_principal=DisciplineEnum.OBRAS_TERRA, valor_global=Decimal('100000.00'), validade=date.today(), status=ProposalStatusEnum.APROVADA)
        contract = prop.contract

        # Medição 1: R$ 60.000 (Válida)
        m1 = MeasurementSheet.objects.create(contrato=contract, competencia=date(2026, 8, 1), valor_total_medido=Decimal('60000.00'), status=MeasurementStatusEnum.APROVADA_CLIENTE)
        self.assertEqual(m1.numero_medicao, 1)

        # Medição 2: R$ 50.000 (Ultrapassa o saldo restante de R$ 40.000) -> Erro
        m2_invalid = MeasurementSheet(contrato=contract, competencia=date(2026, 9, 1), valor_total_medido=Decimal('50000.00'))
        with self.assertRaises(ValidationError):
            m2_invalid.full_clean()

        # Emissão de NFS-e para medição aprovada
        nf = ServiceInvoice.objects.create(
            medicao=m1,
            numero_nfse='NFS-101',
            valor_bruto=Decimal('60000.00'),
            aliquota_iss=Decimal('5.00'),
            valor_liquido=Decimal('57000.00'),
            status=InvoiceStatusEnum.EMITIDA
        )
        m1.refresh_from_db()
        self.assertEqual(m1.status, MeasurementStatusEnum.FATURADA)
        
        # Parcela gerada
        self.assertEqual(nf.receivables.count(), 1)
        rec = nf.receivables.first()
        self.assertEqual(rec.valor_parcela, Decimal('57000.00'))

        # Cancelamento estorna medição e remove parcelas
        nf.cancel_invoice()
        m1.refresh_from_db()
        self.assertEqual(m1.status, MeasurementStatusEnum.APROVADA_CLIENTE)
        self.assertEqual(nf.receivables.count(), 0)

    # 4. TESTES DE GESTÃO FINANCEIRA (CONTAS A PAGAR)
    def test_financial_approval_threshold_and_liquidation(self):
        # Despesa > R$ 5.000 entra retida
        ap = AccountPayable.objects.create(
            fornecedor=self.contact,
            centro_de_custo=CostCenterEnum.OPERACIONAL_GEOTECNIA,
            categoria_despesa='Sondagens',
            descricao='Serviço de Perforação',
            valor_nominal=Decimal('9000.00'),
            data_vencimento=date(2026, 11, 1)
        )
        self.assertEqual(ap.status, PayableStatusEnum.AGUARDANDO_APROVACAO)

        # Tentativa de liquidar sem comprovante deve falhar
        ap.status = PayableStatusEnum.LIQUIDADA
        with self.assertRaises(ValidationError):
            ap.full_clean()

        # Comprovante anexado permite liquidação
        ap.comprovante_pagamento = SimpleUploadedFile("rec.pdf", b"%PDF...", content_type="application/pdf")
        ap.data_pagamento = date.today()
        ap.full_clean()
        ap.save()
        self.assertEqual(ap.status, PayableStatusEnum.LIQUIDADA)

    # 5. TESTE DE AUDITORIA IMUTÁVEL
    def test_audit_log_records_activity(self):
        initial_logs = ActivityLog.objects.count()
        Contact.objects.create(
            tipo_pessoa=PersonTypeEnum.PF,
            razao_social_nome='Engenheiro Consultor Teste',
            cpf_cnpj='11122233344',
            classificacoes=['PARCEIRO']
        )
        # O signal deve ter registrado a mutação
        self.assertGreater(ActivityLog.objects.count(), initial_logs)
