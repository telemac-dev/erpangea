import uuid
import hashlib
from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.contacts.models import Contact

class ServiceTypeChoices(models.TextChoices):
    FUNDACOES = 'FUNDACOES', _('Dimensionamento de Fundações Superficiais e Profundas (NBR 6122 / NBR 6118)')
    ESTABILIDADE_TALUDES = 'ESTABILIDADE_TALUDES', _('Análise de Estabilidade de Encostas e Taludes (NBR 11682)')
    CONTENCOES = 'CONTENCOES', _('Projetos Geotécnicos e Estruturais de Contenções de Divisa')
    CONSULTORIA_PERICIA = 'CONSULTORIA_PERICIA', _('Consultoria Geotécnica e Laudos Periciais em Obra')

class ProposalStatusChoices(models.TextChoices):
    RASCUNHO = 'RASCUNHO', _('Rascunho')
    ENVIADA = 'ENVIADA', _('Enviada ao Cliente')
    EM_REVISAO = 'EM_REVISAO', _('Em Revisão Solicitada pelo Cliente')
    ACEITA = 'ACEITA', _('Aceita pelo Cliente (Aprovada)')
    DECLINADA = 'DECLINADA', _('Recusada pelo Cliente')
    EXPIRADA = 'EXPIRADA', _('Validade Expirada')

class InputItemTypeChoices(models.TextChoices):
    SONDAGEM_SPT = 'SONDAGEM_SPT', _('Furos de Sondagem SPT segundo a NBR 6484')
    PLANTA_CARGAS = 'PLANTA_CARGAS', _('Planta de Cargas com Esforços Axiais, Horizontais e Momentos')
    ARQUITETURA_DWG = 'ARQUITETURA_DWG', _('Projetos Arquitetônicos e Implantação em formato DWG')
    LEVANTAMENTO_TOPOGRAFICO = 'LEVANTAMENTO_TOPOGRAFICO', _('Levantamento Planialtimétrico Cadastral (DWG)')
    PROJETO_ESTRUTURAL_DWG = 'PROJETO_ESTRUTURAL_DWG', _('Projeto Estrutural de Concreto ou Estrutura Metálica (DWG)')
    OUTRO = 'OUTRO', _('Outro Documento / Insumo Técnico')

class InputStatusChoices(models.TextChoices):
    PENDENTE = 'PENDENTE', _('Pendente de Entrega pelo Cliente')
    EM_ANALISE = 'EM_ANALISE', _('Em Análise Técnica pelo Geotécnico')
    APROVADO = 'APROVADO', _('Aprovado pelo Responsável Técnico')
    REJEITADO = 'REJEITADO', _('Inconforme / Rejeitado (Exige Nova Emissão)')

class ContractTypeChoices(models.TextChoices):
    PADRAO_ERP = 'PADRAO_ERP', _('Minuta Padrão ERPangea')
    MINUTA_CLIENTE = 'MINUTA_CLIENTE', _('Contrato Externo (Minuta do Cliente)')

class ContractStatusChoices(models.TextChoices):
    MINUTA = 'MINUTA', _('Minuta em Elaboração')
    AGUARDANDO_ASSINATURA = 'AGUARDANDO_ASSINATURA', _('Aguardando Assinatura')
    ASSINADO = 'ASSINADO', _('Contrato Assinado')
    PENDENTE_INSUMOS = 'PENDENTE_INSUMOS', _('Pendente de Insumos da Contratante')
    MISE_EN_SERVICE = 'MISE_EN_SERVICE', _('Em Execução (Mise en Service Ativo - D0)')
    CONCLUIDO = 'CONCLUIDO', _('Concluído e Entregue')
    CANCELADO = 'CANCELADO', _('Cancelado')

def generate_proposal_code(year=None):
    if year is None:
        year = date.today().year
    prefix = f"PROP-"
    suffix = f"A/{year}"
    # Busca o maior sequencial no ano
    last_prop = CommercialProposal.objects.filter(
        proposal_code__endswith=f"/{year}"
    ).order_by('-created_at').first()

    next_num = 1001
    if last_prop and last_prop.proposal_code:
        try:
            # Ex: PROP-1001A/2026 -> 1001
            part = last_prop.proposal_code.replace("PROP-", "").split("A/")[0]
            next_num = int(part) + 1
        except Exception:
            next_num = CommercialProposal.objects.filter(created_at__year=year).count() + 1001

    return f"PROP-{next_num:04d}{suffix}"

class CommercialProposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal_code = models.CharField(
        _('Código da Proposta'),
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('Padrão formal Pangea: PROP-XXXXA/AAAA (ex: PROP-1685A/2026)')
    )
    client = models.ForeignKey(
        Contact,
        on_delete=models.PROTECT,
        related_name='proposals',
        verbose_name=_('Cliente / Contratante')
    )
    project_name = models.CharField(_('Nome da Obra / Empreendimento'), max_length=255, db_index=True)
    project_location = models.CharField(_('Localização da Obra'), max_length=255, default='Manaus/AM')
    
    # Responsáveis internos
    salesperson = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='commercial_proposals',
        verbose_name=_('Consultor Comercial')
    )
    technical_responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='technical_proposals',
        verbose_name=_('Responsável Técnico (Engenheiro com CREA)')
    )

    # Condições contratuais
    validity_days = models.PositiveIntegerField(_('Prazo de Validade (Dias)'), default=30)
    execution_lead_time_days = models.PositiveIntegerField(
        _('Prazo de Execução (Dias Corridos a partir de D0)'),
        default=20,
        help_text=_('Contagem estritamente suspensa até a aprovação de todos os insumos da contratante.')
    )
    total_value = models.DecimalField(_('Valor Global (R$)'), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_terms_desc = models.TextField(
        _('Forma de Pagamento e Condições'),
        default='50% de entrada no aceite da proposta e 50% na entrega final do projeto executivo.'
    )

    # Ciclo de vida e status
    status = models.CharField(
        _('Status da Proposta'),
        max_length=25,
        choices=ProposalStatusChoices.choices,
        default=ProposalStatusChoices.RASCUNHO,
        db_index=True
    )
    public_token = models.UUIDField(
        _('Token de Acesso Público'),
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )

    # Datas de controle
    sent_at = models.DateTimeField(_('Enviada ao Cliente em'), null=True, blank=True)
    expires_at = models.DateField(_('Data Limite de Validade'), blank=True, null=True, db_index=True)

    # Dados do Aceite Eletrônico Legal (MP 2.200-2/2001 e Lei 14.063/2020)
    accepted_at = models.DateTimeField(_('Aceita em'), null=True, blank=True)
    acceptance_signer_name = models.CharField(_('Nome do Signatário'), max_length=150, blank=True)
    acceptance_signer_doc = models.CharField(_('CPF/CNPJ do Signatário'), max_length=25, blank=True)
    acceptance_signer_role = models.CharField(_('Cargo / Função do Signatário'), max_length=100, blank=True)
    acceptance_ip = models.GenericIPAddressField(_('Endereço IP do Aceite'), null=True, blank=True)
    acceptance_user_agent = models.TextField(_('Navegador / Dispositivo'), blank=True)
    acceptance_hash = models.CharField(_('Hash SHA-256 do Manifesto'), max_length=64, blank=True)

    # Tratamento de recusa ou contraproposta
    rejection_reason = models.TextField(_('Motivo da Recusa'), blank=True)
    revision_notes = models.TextField(_('Comentários de Revisão da Contratante'), blank=True)

    # Desbloqueio por alçada superior
    unlocked_at = models.DateTimeField(_('Desbloqueada em'), null=True, blank=True)
    unlocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unlocked_proposals',
        verbose_name=_('Desbloqueada Por')
    )
    unlock_reason = models.TextField(_('Justificativa do Desbloqueio'), blank=True)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    class Meta:
        verbose_name = _('Proposta Comercial')
        verbose_name_plural = _('Propostas Comerciais')
        ordering = ['-created_at']

    def is_expired(self):
        if self.expires_at and self.expires_at < timezone.now().date():
            return True
        return False

    def clean(self):
        super().clean()
        # Se ja foi aceita, trava valores e parametros essenciais
        if not self._state.adding and self.pk:
            old = CommercialProposal.objects.filter(pk=self.pk).first()
            if old and old.status == ProposalStatusChoices.ACEITA and self.status == ProposalStatusChoices.ACEITA:
                if old.total_value != self.total_value:
                    raise ValidationError({'total_value': _("Não é permitido alterar o valor global de uma proposta comercial já aceita e formalizada.")})
                if old.client_id != self.client_id:
                    raise ValidationError({'client': _("Não é permitido alterar o cliente de uma proposta já aceita.")})

    def save(self, *args, **kwargs):
        if not self.proposal_code:
            self.proposal_code = generate_proposal_code()
        
        # Calcula data de expiracao se nao definida
        if not self.expires_at:
            ref_date = self.sent_at.date() if self.sent_at else date.today()
            self.expires_at = ref_date + timedelta(days=self.validity_days)

        self.clean()
        super().save(*args, **kwargs)

    def calculate_totals(self):
        total = self.scope_items.aggregate(s=models.Sum('subtotal_value'))['s'] or Decimal('0.00')
        if total > Decimal('0.00'):
            self.total_value = total
            self.save(update_fields=['total_value'])
        return self.total_value

    def accept_online(self, signer_name, signer_doc, signer_role, ip_address, user_agent):
        if self.is_expired():
            self.status = ProposalStatusChoices.EXPIRADA
            self.save(update_fields=['status'])
            raise ValidationError(_("Esta proposta comercial atingiu a data limite de validade e está expirada."))

        now = timezone.now()
        # Gera hash SHA-256 auditável
        hash_payload = f"{self.proposal_code}|{self.client.name}|{self.total_value}|{now.isoformat()}|{signer_doc}|{ip_address}"
        doc_hash = hashlib.sha256(hash_payload.encode('utf-8')).hexdigest()

        self.status = ProposalStatusChoices.ACEITA
        self.accepted_at = now
        self.acceptance_signer_name = signer_name
        self.acceptance_signer_doc = signer_doc
        self.acceptance_signer_role = signer_role
        self.acceptance_ip = ip_address
        self.acceptance_user_agent = user_agent[:500]
        self.acceptance_hash = doc_hash
        self.save()

        # Cria ou atualiza automaticamente a Minuta de Contrato
        contract = self.create_contract_draft()
        return contract

    def create_contract_draft(self):
        if hasattr(self, 'contract'):
            return self.contract

        contract_code = self.proposal_code.replace("PROP-", "CTR-")
        
        # Gera as cláusulas padrão da Pangea Engenharia
        clauses_html = f"""
        <h4>CONTRATO DE PRESTAÇÃO DE SERVIÇOS TÉCNICOS DE ENGENHARIA CONSULTIVA</h4>
        <p><strong>CONTRATO Nº:</strong> {contract_code}</p>
        <p><strong>CONTRATADA:</strong> PANGEA ENGENHARIA LTDA., pessoa jurídica de direito privado, inscrita no CNPJ sob o nº 12.345.678/0001-90, com sede na Comarca de Manaus, Estado do Amazonas.</p>
        <p><strong>CONTRATANTE:</strong> {self.client.name}, inscrita sob o CNPJ/CPF nº {self.client.formatted_doc_number or self.client.doc_number}, com sede/domicílio em {self.client.display_address}.</p>
        
        <h5>CLÁUSULA PRIMEIRA – DO OBJETO E ESCOPO</h5>
        <p>1.1. O presente instrumento tem por objeto a prestação de serviços especializados de consultoria e projetos de engenharia civil e geotécnica para a obra <strong>{self.project_name}</strong>, localizada em {self.project_location}.</p>
        <p>1.2. O escopo compreende estritamente os serviços parametrizados na Proposta Comercial Técnica {self.proposal_code}, regidos pelas seguintes normas da ABNT: NBR 6122 (Projeto e Execução de Fundações), NBR 6118 (Estruturas de Concreto Armado) e NBR 11682 (Estabilidade de Encostas).</p>
        
        <h5>CLÁUSULA SEGUNDA – DO PREÇO E CONDIÇÕES DE PAGAMENTO</h5>
        <p>2.1. Pelos serviços contratados, a CONTRATANTE pagará à CONTRATADA o valor global fixo e irreajustável de <strong>R$ {self.total_value:,.2f}</strong>.</p>
        <p>2.2. Forma de pagamento: {self.payment_terms_desc}</p>
        
        <h5>CLÁUSULA TERCEIRA – DA CONDIÇÃO SUSPENSIVA DE PRAZO (MISE EN SERVICE)</h5>
        <p>3.1. O prazo de execução pactuado é de <strong>{self.execution_lead_time_days} dias corridos</strong>.</p>
        <p>3.2. <strong>CONDIÇÃO SUSPENSIVA EXPRESSA:</strong> Fica expressamente convencionado que a contagem do prazo de execução somente terá início a partir da data de entrega integral e validação técnica de todos os insumos obrigatórios de responsabilidade da CONTRATANTE (sondagens SPT conforme NBR 6484, plantas de carga com momentos e arquivos DWG), formalizando o marco zero ($D_0$) emitido pelo sistema ERPangea.</p>
        
        <h5>CLÁUSULA QUARTA – DA RESPONSABILIDADE TÉCNICA E ART</h5>
        <p>4.1. A CONTRATADA providenciará a competente Anotação de Responsabilidade Técnica (ART) junto ao CREA-AM.</p>
        
        <h5>CLÁUSULA QUINTA – DO FORO</h5>
        <p>5.1. Para dirimir quaisquer litígios oriundos do presente contrato, as partes elegem o Foro da Comarca de Manaus/AM, com renúncia expressa a qualquer outro, por mais privilegiado que seja.</p>
        """

        contract = LegalContract.objects.create(
            proposal=self,
            contract_code=contract_code,
            contract_type=ContractTypeChoices.PADRAO_ERP,
            contract_html_body=clauses_html.strip(),
            status=ContractStatusChoices.MINUTA
        )
        return contract

    def unlock(self, user, reason=""):
        """
        Desbloqueia uma proposta comercial aceita, retornando-a para o status de EM_REVISAO.
        Exige autorização de nível elevado (Coordenação/Diretoria ou Superusuário).
        Registra a auditoria, usuário responsável, data e justificativa.
        """
        from apps.accounts.permissions import can_unlock_proposal
        from apps.audit_log.models import AuditLog, AuditActionChoices

        if self.status != ProposalStatusChoices.ACEITA:
            raise ValidationError(_("Apenas propostas com status 'Aceita' podem ser desbloqueadas."))

        if not can_unlock_proposal(user):
            raise PermissionDenied(_("Acesso negado: seu perfil não possui alçada hierárquica suficiente (Coordenação ou Diretoria) para desbloquear uma proposta aceita."))

        reason = (reason or "").strip()
        if not reason:
            raise ValidationError({'unlock_reason': _("A justificativa do desbloqueio é obrigatória para fins de governança e auditoria.")})

        self.status = ProposalStatusChoices.EM_REVISAO
        self.unlocked_at = timezone.now()
        self.unlocked_by = user
        self.unlock_reason = reason
        self.save(update_fields=['status', 'unlocked_at', 'unlocked_by', 'unlock_reason'])

        AuditLog.objects.create(
            user=user,
            action=AuditActionChoices.UPDATE,
            app_label='commercial',
            model_name='commercialproposal',
            object_id=str(self.pk),
            object_repr=f"Desbloqueio de Proposta {self.proposal_code}",
            changes={
                'status': [ProposalStatusChoices.ACEITA, ProposalStatusChoices.EM_REVISAO],
                'unlocked_by': getattr(user, 'email', str(user)),
                'reason': reason
            }
        )

    def __str__(self):
        return f"{self.proposal_code} - {self.client.name} ({self.get_status_display()})"

class TechnicalDiscipline(models.Model):
    """
    Disciplina técnica de engenharia (Geotecnia, Fundações, Estruturas, Contenções, Obras de Terra, etc.)
    Permite criação dinâmica no banco e inline na proposta.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Nome da Disciplina'), max_length=120, unique=True)
    description = models.TextField(_('Descrição'), blank=True)
    is_active = models.BooleanField(_('Ativo'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Disciplina Técnica')
        verbose_name_plural = _('Disciplinas Técnicas')
        ordering = ['name']

    def __str__(self):
        return self.name


class TechnicalServiceType(models.Model):
    """
    Tipo de Serviço técnico prestado pela Pangea Engenharia.
    Permite criação dinâmica no banco e inline na proposta.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discipline = models.ForeignKey(
        TechnicalDiscipline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_types',
        verbose_name=_('Disciplina')
    )
    name = models.CharField(_('Tipo de Serviço'), max_length=180, unique=True)
    code = models.CharField(_('Código de Referência'), max_length=50, blank=True)
    default_nbr_references = models.CharField(
        _('Normas ABNT Padrão'),
        max_length=150,
        blank=True,
        help_text=_('Ex: ABNT NBR 6122:2019 e NBR 6118:2023')
    )
    default_description = models.TextField(_('Memorial Descritivo Padrão'), blank=True)
    is_active = models.BooleanField(_('Ativo'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Tipo de Serviço Técnico')
        verbose_name_plural = _('Tipos de Serviços Técnicos')
        ordering = ['name']

    def __str__(self):
        if self.discipline:
            return f"{self.discipline.name} - {self.name}"
        return self.name


class TechnicalInputType(models.Model):
    """
    Tipo de insumo técnico de fornecimento obrigatório pela Contratante (Mise en Service / D0).
    Permite criação dinâmica no banco e inline na proposta.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Tipo de Insumo'), max_length=180, unique=True)
    code = models.CharField(_('Código de Referência'), max_length=50, blank=True)
    default_description = models.CharField(
        _('Especificação Técnica Mínima'),
        max_length=255,
        blank=True,
        default='Fornecimento obrigatório pela contratante conforme normas técnicas.'
    )
    is_mandatory_default = models.BooleanField(_('Bloqueia D0 por Padrão'), default=True)
    is_active = models.BooleanField(_('Ativo'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Tipo de Insumo Técnico')
        verbose_name_plural = _('Tipos de Insumos Técnicos')
        ordering = ['name']

    def __str__(self):
        return self.name


class ProposalScopeItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(CommercialProposal, on_delete=models.CASCADE, related_name='scope_items')
    
    discipline = models.ForeignKey(
        TechnicalDiscipline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scope_items',
        verbose_name=_('Disciplina')
    )
    service_type_ref = models.ForeignKey(
        TechnicalServiceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scope_items',
        verbose_name=_('Tipo de Serviço')
    )
    service_type = models.CharField(_('Disciplina / Serviço'), max_length=180, blank=True)
    nbr_references = models.CharField(
        _('Normas ABNT Aplicáveis'),
        max_length=150,
        blank=True,
        default='',
        help_text=_('Ex: ABNT NBR 6122:2019 e NBR 6118:2023')
    )
    description = models.TextField(_('Memorial Descritivo do Escopo'))
    subtotal_value = models.DecimalField(_('Subtotal (R$)'), max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = _('Item de Escopo da Proposta')
        verbose_name_plural = _('Itens de Escopo da Proposta')
        ordering = ['service_type']

    def save(self, *args, **kwargs):
        if self.service_type_ref and not self.service_type:
            self.service_type = self.service_type_ref.name
        super().save(*args, **kwargs)
        self.proposal.calculate_totals()

    def delete(self, *args, **kwargs):
        proposal = self.proposal
        super().delete(*args, **kwargs)
        proposal.calculate_totals()

    def get_service_type_display(self):
        if self.service_type_ref:
            return self.service_type_ref.name
        choices_map = dict(ServiceTypeChoices.choices)
        return choices_map.get(self.service_type, self.service_type or '')
    def __str__(self):
        return f"{self.get_service_type_display()} - R$ {self.subtotal_value}"


class ProposalInputRequirement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(CommercialProposal, on_delete=models.CASCADE, related_name='input_requirements')
    
    input_type_ref = models.ForeignKey(
        TechnicalInputType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requirements',
        verbose_name=_('Tipo do Insumo')
    )
    required_item_type = models.CharField(_('Insumo Obrigatório'), max_length=180, blank=True)
    description = models.CharField(
        _('Especificação Técnica Mínima'),
        max_length=255,
        default='Fornecimento obrigatório pela contratante conforme normas técnicas.'
    )
    is_mandatory = models.BooleanField(_('Bloqueia Início das Obras (D0)'), default=True)
    status = models.CharField(_('Situação'), max_length=20, choices=InputStatusChoices.choices, default=InputStatusChoices.PENDENTE)
    
    # Arquivo recebido do cliente
    uploaded_file = models.FileField(_('Arquivo Recebido'), upload_to='commercial/inputs/', null=True, blank=True)
    technical_notes = models.TextField(_('Parecer do Engenheiro Geotécnico'), blank=True)
    validated_at = models.DateTimeField(_('Homologado em'), null=True, blank=True)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_inputs',
        verbose_name=_('Validado Por')
    )

    class Meta:
        verbose_name = _('Insumo Técnico Obrigatório')
        verbose_name_plural = _('Insumos Técnicos Obrigatórios')
        ordering = ['required_item_type']

    def save(self, *args, **kwargs):
        if self.input_type_ref and not self.required_item_type:
            self.required_item_type = self.input_type_ref.name
        super().save(*args, **kwargs)

    def get_required_item_type_display(self):
        if self.input_type_ref:
            return self.input_type_ref.name
        choices_map = dict(InputItemTypeChoices.choices)
        return choices_map.get(self.required_item_type, self.required_item_type or _('Insumo Técnico'))

    def approve_input(self, engineer_user, notes='Conforme com as normas ABNT aplicáveis.'):
        self.status = InputStatusChoices.APROVADO
        self.validated_by = engineer_user
        self.validated_at = timezone.now()
        self.technical_notes = notes
        self.save()

    def reject_input(self, engineer_user, reason):
        self.status = InputStatusChoices.REJEITADO
        self.validated_by = engineer_user
        self.validated_at = timezone.now()
        self.technical_notes = reason
        self.save()

    def __str__(self):
        return f"[{self.get_status_display()}] {self.get_required_item_type_display()}"
class LegalContract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.OneToOneField(CommercialProposal, on_delete=models.PROTECT, related_name='contract')
    contract_code = models.CharField(_('Código do Contrato'), max_length=50, unique=True, db_index=True)
    contract_type = models.CharField(_('Modelo de Minuta'), max_length=20, choices=ContractTypeChoices.choices, default=ContractTypeChoices.PADRAO_ERP)
    contract_html_body = models.TextField(_('Texto das Cláusulas Contratuais'))
    status = models.CharField(
        _('Situação do Contrato'),
        max_length=25,
        choices=ContractStatusChoices.choices,
        default=ContractStatusChoices.MINUTA,
        db_index=True
    )

    # Documento Assinado (PDF)
    signed_pdf = models.FileField(_('Contrato Assinado (PDF)'), upload_to='commercial/contracts/', null=True, blank=True)
    signed_at = models.DateField(_('Data de Assinatura'), null=True, blank=True)

    # ART do CREA-AM
    crea_art_number = models.CharField(_('Número da ART no CREA-AM'), max_length=50, blank=True, help_text=_('Registro de Anotação de Responsabilidade Técnica'))
    crea_art_file = models.FileField(_('Comprovante da ART'), upload_to='commercial/arts/', null=True, blank=True)
    crea_art_status = models.CharField(_('Status da ART'), max_length=20, default='PENDENTE')

    # Gatilho de Entrada em Serviço (Mise en Service)
    d0_trigger_date = models.DateField(_('Marco Zero (D0)'), null=True, blank=True, help_text=_('Início efetivo da contagem do prazo contratual'))
    deadline_date = models.DateField(_('Data Final de Entrega do Projeto'), null=True, blank=True)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Contrato Formal')
        verbose_name_plural = _('Contratos Formais')
        ordering = ['-created_at']

    def can_trigger_mise_en_service(self):
        """
        Gatilho de Governança: Retorna (pode_iniciar: bool, lista_de_pendencias: list)
        Exige rigorosamente:
        1. Contrato assinado (status ASSINADO ou com signed_pdf anexado).
        2. Todos os insumos obrigatórios do cliente APROVADOS pelo geotécnico.
        3. Registro da ART no CREA-AM informado.
        """
        pendencias = []

        # 1. Contrato Assinado
        if not self.signed_pdf and self.status not in (ContractStatusChoices.ASSINADO, ContractStatusChoices.PENDENTE_INSUMOS, ContractStatusChoices.MISE_EN_SERVICE):
            pendencias.append(_("Contrato ainda não possui o documento formal assinado anexado."))

        # 2. Insumos Técnicos Obrigatórios
        unapproved_inputs = self.proposal.input_requirements.filter(
            is_mandatory=True
        ).exclude(status=InputStatusChoices.APROVADO)

        if unapproved_inputs.exists():
            for inp in unapproved_inputs:
                pendencias.append(_(f"Insumo técnico pendente de validação: {inp.get_required_item_type_display()} ({inp.get_status_display()})"))

        # 3. ART CREA-AM
        if not self.crea_art_number:
            pendencias.append(_("Número de ART do CREA-AM ainda não registrado."))

        return len(pendencias) == 0, pendencias

    def trigger_mise_en_service(self, authorized_user):
        can_start, pendencias = self.can_trigger_mise_en_service()
        if not can_start:
            raise ValidationError({'status': _("Mise en Service bloqueado: ") + "; ".join(str(p) for p in pendencias)})

        d0 = timezone.now().date()
        lead_time = self.proposal.execution_lead_time_days
        
        self.d0_trigger_date = d0
        self.deadline_date = d0 + timedelta(days=lead_time)
        self.status = ContractStatusChoices.MISE_EN_SERVICE
        self.save(update_fields=['d0_trigger_date', 'deadline_date', 'status', 'updated_at'])
        return self.d0_trigger_date, self.deadline_date

    def __str__(self):
        return f"{self.contract_code} - {self.proposal.project_name} ({self.get_status_display()})"
