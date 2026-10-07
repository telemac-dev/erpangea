from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
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
    TechnicalDiscipline,
    TechnicalServiceType,
    TechnicalInputType
)

User = get_user_model()

class Command(BaseCommand):
    help = "Popula propostas comerciais, escopos técnicos com normas ABNT e contratos de demonstração"

    def handle(self, *args, **options):
        self.stdout.write("==> Populando dados de demonstração do módulo Comercial & Contratos...")

        user_admin = User.objects.filter(is_staff=True).first()
        client_alianca = Contact.objects.filter(name__icontains="Aliança").first()
        client_camargo = Contact.objects.filter(name__icontains="Camargo").first()
        client_vale = Contact.objects.filter(name__icontains="Vale").first()

        if not client_alianca:
            client_alianca = Contact.objects.create(name="Construtora Aliança S.A.", contact_type=ContactTypeChoices.COMPANY)
        if not client_camargo:
            client_camargo = Contact.objects.create(name="Camargo Corrêa Obras Ltda", contact_type=ContactTypeChoices.COMPANY)
        if not client_vale:
            client_vale = Contact.objects.create(name="Vale Mineração S.A.", contact_type=ContactTypeChoices.COMPANY)

        # 1. Proposta 1: Criada primeiro como Rascunho, itens adicionados, e depois Aceita formalmente
        p1, created1 = CommercialProposal.objects.get_or_create(
            proposal_code="PROP-1685A/2026",
            defaults={
                'client': client_alianca,
                'project_name': "Contenção de Encosta e Solo Grampeado - Porto Fluvial",
                'project_location': "Estrada do Brito, Ponta Negra, Manaus/AM",
                'salesperson': user_admin,
                'technical_responsible': user_admin,
                'validity_days': 30,
                'execution_lead_time_days': 25,
                'status': ProposalStatusChoices.RASCUNHO,
                'sent_at': timezone.now() - timedelta(days=10),
                'expires_at': timezone.now().date() + timedelta(days=20),
                'payment_terms_desc': "50% de entrada no aceite e 50% na emissão do relatório final com ART."
            }
        )
        if not hasattr(p1, "contract"):
            st_cont = TechnicalServiceType.objects.filter(name__icontains="Contenções").first()
            st_talu = TechnicalServiceType.objects.filter(name__icontains="Taludes").first()

            ProposalScopeItem.objects.create(
                proposal=p1,
                service_type_ref=st_cont,
                discipline=st_cont.discipline if st_cont else None,
                service_type=st_cont.name if st_cont else ServiceTypeChoices.CONTENCOES,
                nbr_references="ABNT NBR 11682:2009 e NBR 6118:2023",
                description="Projeto executivo de contenção em cortina de solo grampeado com concreto projetado e drenagem profunda subsuperficial.",
                subtotal_value=Decimal('42000.00')
            )
            ProposalScopeItem.objects.create(
                proposal=p1,
                service_type_ref=st_talu,
                discipline=st_talu.discipline if st_talu else None,
                service_type=st_talu.name if st_talu else ServiceTypeChoices.ESTABILIDADE_TALUDES,
                nbr_references="ABNT NBR 11682:2009",
                description="Análise de estabilidade global de talude com cálculo de fatores de segurança (Bishop simplificado e Morgenstern-Price).",
                subtotal_value=Decimal('18000.00')
            )
            # Insumos técnicos
            inp_spt = TechnicalInputType.objects.filter(name__icontains="Sondagem SPT").first()
            inp_arq = TechnicalInputType.objects.filter(name__icontains="Arquitetônicos").first()
            inp_carg = TechnicalInputType.objects.filter(name__icontains="Cargas").first()

            ProposalInputRequirement.objects.create(
                proposal=p1,
                input_type_ref=inp_spt,
                required_item_type=inp_spt.name if inp_spt else InputItemTypeChoices.SONDAGEM_SPT,
                description="Laudo de Sondagem SPT com 4 furos segundo NBR 6484",
                is_mandatory=True,
                status=InputStatusChoices.APROVADO,
                validated_by=user_admin,
                validated_at=timezone.now() - timedelta(days=2),
                technical_notes="Laudo aprovado com N-SPT satisfatório para dimensionamento."
            )
            ProposalInputRequirement.objects.create(
                proposal=p1,
                input_type_ref=inp_arq,
                required_item_type=inp_arq.name if inp_arq else InputItemTypeChoices.ARQUITETURA_DWG,
                description="Plantas em formato DWG com curvas de nível e implantação",
                is_mandatory=True,
                status=InputStatusChoices.APROVADO,
                validated_by=user_admin,
                validated_at=timezone.now() - timedelta(days=2),
                technical_notes="Arquivos CAD compatíveis e cotas validadas."
            )
            ProposalInputRequirement.objects.create(
                proposal=p1,
                input_type_ref=inp_carg,
                required_item_type=inp_carg.name if inp_carg else InputItemTypeChoices.PLANTA_CARGAS,
                description="Planta de cargas axiais e momentos do pátio",
                is_mandatory=True,
                status=InputStatusChoices.APROVADO,
                validated_by=user_admin,
                validated_at=timezone.now() - timedelta(days=2),
                technical_notes="Esforços estruturais verificados."
            )
            # Aceite formal do cliente
            p1.status = ProposalStatusChoices.ACEITA
            p1.accepted_at = timezone.now() - timedelta(days=3)
            p1.acceptance_signer_name = "Eng. Eduardo Rezende"
            p1.acceptance_signer_doc = "11222333000181"
            p1.acceptance_signer_role = "Diretor de Operações"
            p1.acceptance_ip = "187.19.220.45"
            p1.acceptance_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0"
            p1.acceptance_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            p1.save()

            # Contrato com Mise en Service ativo
            c1 = p1.create_contract_draft()
            c1.crea_art_number = "ART-CREA-AM-2026-009988"
            c1.status = ContractStatusChoices.MISE_EN_SERVICE
            c1.d0_trigger_date = timezone.now().date() - timedelta(days=2)
            c1.deadline_date = c1.d0_trigger_date + timedelta(days=p1.execution_lead_time_days)
            c1.save()

        # 2. Proposta 2: Enviada (Pronta para o cliente testar aceite na Landing Page)
        p2, created2 = CommercialProposal.objects.get_or_create(
            proposal_code="PROP-1686A/2026",
            defaults={
                'client': client_camargo,
                'project_name': "Dimensionamento de Fundações em Hélice Contínua e Radier",
                'project_location': "Avenida Coronel Teixeira, Ponta Negra, Manaus/AM",
                'salesperson': user_admin,
                'technical_responsible': user_admin,
                'validity_days': 30,
                'execution_lead_time_days': 20,
                'status': ProposalStatusChoices.RASCUNHO,
                'sent_at': timezone.now() - timedelta(days=2),
                'expires_at': timezone.now().date() + timedelta(days=28),
                'payment_terms_desc': "30% no aceite, 30% na entrega preliminar de fundações e 40% no memorial final."
            }
        )
        if p2.scope_items.count() == 0:
            ProposalScopeItem.objects.create(
                proposal=p2,
                service_type=ServiceTypeChoices.FUNDACOES,
                nbr_references="ABNT NBR 6122:2019 e NBR 6118:2023",
                description="Projeto executivo completo de fundações em estacas tipo hélice contínua monitorada e blocos de coroamento em concreto armado.",
                subtotal_value=Decimal('55000.00')
            )
            ProposalInputRequirement.objects.create(
                proposal=p2,
                required_item_type=InputItemTypeChoices.SONDAGEM_SPT,
                description="Sondagens a percussão SPT com medição do nível do lençol freático (NBR 6484).",
                is_mandatory=True,
                status=InputStatusChoices.PENDENTE
            )
            ProposalInputRequirement.objects.create(
                proposal=p2,
                required_item_type=InputItemTypeChoices.PLANTA_CARGAS,
                description="Planta de cargas com tabela de esforços axiais característicos e momentos fletores.",
                is_mandatory=True,
                status=InputStatusChoices.PENDENTE
            )
            p2.status = ProposalStatusChoices.ENVIADA
            p2.save()

        # 3. Proposta 3: Rascunho Interno
        p3, created3 = CommercialProposal.objects.get_or_create(
            proposal_code="PROP-1687A/2026",
            defaults={
                'client': client_vale,
                'project_name': "Consultoria e Parecer Técnico de Estabilidade de Dique",
                'project_location': "Complexo Industrial e Minerário, Itacoatiara/AM",
                'salesperson': user_admin,
                'technical_responsible': user_admin,
                'validity_days': 15,
                'execution_lead_time_days': 15,
                'status': ProposalStatusChoices.RASCUNHO,
                'payment_terms_desc': "100% após entrega e homologação do parecer técnico pericial."
            }
        )
        if p3.scope_items.count() == 0:
            ProposalScopeItem.objects.create(
                proposal=p3,
                service_type=ServiceTypeChoices.CONSULTORIA_PERICIA,
                nbr_references="ABNT NBR 11682 e Manual de Segurança de Barragens",
                description="Vistoria técnica pericial in loco com análise de instrumentação piezométrica e emissão de laudo técnico conclusivo.",
                subtotal_value=Decimal('30000.00')
            )

        self.stdout.write(self.style.SUCCESS(
            f" [OK] Propostas comerciais e contratos de demonstração populados com sucesso!\n"
            f" -> Total de propostas: {CommercialProposal.objects.count()}\n"
            f" -> Proposta Aceita (Contrato & D0 Ativo): {p1.proposal_code}\n"
            f" -> Proposta Enviada (Pronta para Aceite no Portal): {p2.proposal_code} (Token: {p2.public_token})\n"
            f" -> Proposta Rascunho: {p3.proposal_code}"
        ))
