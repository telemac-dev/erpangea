import json
from decimal import Decimal
from datetime import date, timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError, PermissionDenied

from .models import (
    CommercialProposal,
    ProposalScopeItem,
    ProposalInputRequirement,
    LegalContract,
    ProposalStatusChoices,
    ContractStatusChoices,
    InputStatusChoices,
    InputItemTypeChoices,
    InputCategoryChoices,
    ServiceTypeChoices,
    ContractTypeChoices,
    TechnicalDiscipline,
    TechnicalServiceType,
    TechnicalInputType
)
from .forms import (
    ProposalForm,
    ProposalScopeItemForm,
    ProposalInputRequirementForm,
    TechnicalInputValidationForm,
    LegalContractForm,
    OnlineAcceptanceForm,
    ClientRevisionRequestForm,
    ClientRejectionForm
)
from apps.accounts.permissions import RoleRequiredMixin
from apps.audit_log.context import get_client_ip

class ProposalListView(LoginRequiredMixin, ListView):
    model = CommercialProposal
    template_name = 'commercial/proposal_list.html'
    context_object_name = 'proposals'
    paginate_by = 10

    def get_queryset(self):
        qs = CommercialProposal.objects.select_related('client', 'salesperson', 'technical_responsible')
        
        # 1. Filtro de Busca Textual Ampla
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(proposal_code__icontains=q) |
                Q(project_name__icontains=q) |
                Q(project_location__icontains=q) |
                Q(client__name__icontains=q) |
                Q(client__doc_number__icontains=q) |
                Q(scope_items__service_type__icontains=q)
            ).distinct()

        # 2. Filtro de Status da Proposta
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)

        # 3. Filtro de Consultor / Vendedor
        salesperson_id = self.request.GET.get('salesperson', '').strip()
        if salesperson_id:
            qs = qs.filter(salesperson_id=salesperson_id)

        # 4. Filtro de Responsável Técnico
        tech_id = self.request.GET.get('technical_responsible', '').strip()
        if tech_id:
            qs = qs.filter(technical_responsible_id=tech_id)

        # 5. Filtro de Vigência (Vigentes vs Expiradas)
        validity = self.request.GET.get('validity', '').strip()
        today = timezone.now().date()
        if validity == 'valid':
            qs = qs.filter(
                Q(expires_at__gte=today) | Q(expires_at__isnull=True),
                status__in=[
                    ProposalStatusChoices.RASCUNHO,
                    ProposalStatusChoices.ENVIADA,
                    ProposalStatusChoices.EM_REVISAO,
                    ProposalStatusChoices.ACEITA
                ]
            )
        elif validity == 'expired':
            qs = qs.filter(
                Q(expires_at__lt=today) | Q(status=ProposalStatusChoices.EXPIRADA)
            ).exclude(status=ProposalStatusChoices.ACEITA)

        # 6. Ordenação
        ordering = self.request.GET.get('ordering', '-created_at').strip()
        allowed_orderings = {
            '-created_at': '-created_at',
            'created_at': 'created_at',
            '-total_value': '-total_value',
            'total_value': 'total_value',
            'proposal_code': 'proposal_code',
            '-proposal_code': '-proposal_code',
        }
        qs = qs.order_by(allowed_orderings.get(ordering, '-created_at'))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        
        # Parâmetros de filtro ativos
        context['q'] = self.request.GET.get('q', '').strip()
        context['status_filter'] = self.request.GET.get('status', '').strip()
        context['salesperson_filter'] = self.request.GET.get('salesperson', '').strip()
        context['tech_filter'] = self.request.GET.get('technical_responsible', '').strip()
        context['validity_filter'] = self.request.GET.get('validity', '').strip()
        context['ordering'] = self.request.GET.get('ordering', '-created_at').strip()
        
        # Opções de dropdown
        context['statuses'] = ProposalStatusChoices.choices
        context['salespeople'] = User.objects.filter(is_active=True).order_by('first_name', 'email')
        context['technicals'] = User.objects.filter(is_active=True).order_by('first_name', 'email')
        
        # Métricas consolidadas para os cards do topo
        base_qs = CommercialProposal.objects.all()
        total_val = base_qs.filter(status__in=[ProposalStatusChoices.ENVIADA, ProposalStatusChoices.EM_REVISAO]).aggregate(Sum('total_value'))['total_value__sum']
        context['metrics'] = {
            'total': base_qs.count(),
            'negotiation': base_qs.filter(status__in=[ProposalStatusChoices.ENVIADA, ProposalStatusChoices.EM_REVISAO]).count(),
            'accepted': base_qs.filter(status=ProposalStatusChoices.ACEITA).count(),
            'pipeline_value': total_val or Decimal('0.00'),
            'filtered_total': self.get_queryset().count(),
        }

        # Preservação de parâmetros GET para os links de paginação
        params = self.request.GET.copy()
        if 'page' in params:
            del params['page']
        context['query_params'] = params.urlencode()
        
        return context
class ProposalCreateView(LoginRequiredMixin, CreateView):
    model = CommercialProposal
    form_class = ProposalForm
    template_name = 'commercial/proposal_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['salesperson'] = self.request.user
        initial['technical_responsible'] = self.request.user
        return initial

    def form_valid(self, form):
        proposal = form.save()

        # Seed automático dos insumos técnicos mandatórios da Pangea Engenharia
        default_inputs = [
            (InputItemTypeChoices.SONDAGEM_SPT, "Laudo de Sondagem a Percussão SPT conforme ABNT NBR 6484 com no mínimo 3 furos e indicação de N-SPT."),
            (InputItemTypeChoices.PLANTA_CARGAS, "Planta de Cargas com memorial estrutural detalhando esforços axiais (Nk), horizontais (Hx, Hy) e momentos fletores."),
            (InputItemTypeChoices.ARQUITETURA_DWG, "Projeto Arquitetônico completo e Implantação Verticalizada em formato editável DWG."),
        ]
        for req_type, desc in default_inputs:
            ProposalInputRequirement.objects.create(
                proposal=proposal,
                required_item_type=req_type,
                description=desc,
                is_mandatory=True
            )

        messages.success(self.request, _(f"Proposta {proposal.proposal_code} cadastrada com sucesso com checklist de insumos ativado."))
        return redirect('commercial:proposal_detail', pk=proposal.pk)

class ProposalUpdateView(LoginRequiredMixin, UpdateView):
    model = CommercialProposal
    form_class = ProposalForm
    template_name = 'commercial/proposal_form.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status == ProposalStatusChoices.ACEITA:
            messages.error(
                request,
                _("Esta proposta já foi aceita e seus parâmetros estão travados. Para editá-la, um usuário de alçada superior (Coordenação ou Diretoria) deve desbloqueá-la primeiro.")
            )
            return redirect('commercial:proposal_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _("Proposta comercial atualizada com sucesso!"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('commercial:proposal_detail', kwargs={'pk': self.object.pk})


class ProposalDetailView(LoginRequiredMixin, DetailView):
    model = CommercialProposal
    template_name = 'commercial/proposal_detail.html'
    context_object_name = 'proposal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.accounts.permissions import can_unlock_proposal

        context['scope_items'] = self.object.scope_items.all()
        context['input_requirements'] = self.object.input_requirements.all()
        context['contract'] = getattr(self.object, 'contract', None)
        context['scope_form'] = ProposalScopeItemForm()
        context['input_form'] = ProposalInputRequirementForm()
        context['disciplines'] = TechnicalDiscipline.objects.filter(is_active=True).order_by('name')
        context['service_types'] = TechnicalServiceType.objects.filter(is_active=True).order_by('name')
        context['input_types'] = TechnicalInputType.objects.filter(is_active=True).order_by('category', 'name')
        context['can_unlock'] = can_unlock_proposal(self.request.user)
        return context


class ProposalUnlockView(LoginRequiredMixin, View):
    """
    Permite que um usuário de alçada superior (Coordenação, Diretoria ou Superusuário)
    desbloqueie uma proposta comercial aceita, retornando-a para EM_REVISAO para alteração.
    """
    def post(self, request, pk):
        from apps.accounts.permissions import can_unlock_proposal

        proposal = get_object_or_404(CommercialProposal, pk=pk)

        if proposal.status != ProposalStatusChoices.ACEITA:
            messages.warning(request, _("Apenas propostas aceitas e formalizadas necessitam de desbloqueio."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        if not can_unlock_proposal(request.user):
            messages.error(request, _("Acesso negado: seu perfil não possui alçada hierárquica suficiente (Coordenação ou Diretoria) para desbloquear propostas aceitas."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, _("A justificativa técnica/comercial é obrigatória para o desbloqueio da proposta."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        try:
            proposal.unlock(request.user, reason)
            messages.success(
                request,
                _(f"Proposta {proposal.proposal_code} desbloqueada com sucesso por {request.user.get_full_name() or request.user.email} (Alçada Superior). O status retornou para 'Em Revisão' permitindo modificações de escopo, valores e prazos.")
            )
        except (ValidationError, PermissionDenied) as e:
            messages.error(request, str(e))

        return redirect('commercial:proposal_detail', pk=proposal.pk)
class ProposalAddScopeItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        if proposal.status == ProposalStatusChoices.ACEITA:
            messages.error(request, _("Proposta já aceita. O escopo e valores estão travados para alteração."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        form = ProposalScopeItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.proposal = proposal
            item.save()
            messages.success(request, _(f"Item de escopo '{item.get_service_type_display()}' adicionado."))
        else:
            err_msg = "; ".join([f"{f}: {e[0]}" for f, e in form.errors.items()])
            messages.error(request, _(f"Erro ao adicionar item de escopo: {err_msg}"))
        return redirect('commercial:proposal_detail', pk=proposal.pk)


class ProposalEditScopeItemView(LoginRequiredMixin, View):
    """
    Permite modificar um item de escopo técnico parametrizado da proposta.
    """
    def get(self, request, pk, item_id):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        if proposal.status == ProposalStatusChoices.ACEITA:
            messages.error(request, _("Proposta já aceita. O escopo e valores estão travados para alteração."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        item = get_object_or_404(ProposalScopeItem, pk=item_id, proposal=proposal)
        form = ProposalScopeItemForm(instance=item)
        disciplines = TechnicalDiscipline.objects.filter(is_active=True).order_by('name')
        service_types = TechnicalServiceType.objects.filter(is_active=True).order_by('name')
        return render(request, 'commercial/partials/edit_scope_item_modal.html', {
            'proposal': proposal,
            'item': item,
            'form': form,
            'disciplines': disciplines,
            'service_types': service_types,
        })

    def post(self, request, pk, item_id):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        if proposal.status == ProposalStatusChoices.ACEITA:
            messages.error(request, _("Proposta já aceita. O escopo e valores estão travados para alteração."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        item = get_object_or_404(ProposalScopeItem, pk=item_id, proposal=proposal)
        form = ProposalScopeItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=True)
            messages.success(request, _(f"Item de escopo '{item.get_service_type_display()}' modificado com sucesso."))
            if request.headers.get('HX-Request'):
                response = HttpResponse("")
                response['HX-Refresh'] = 'true'
                return response
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        disciplines = TechnicalDiscipline.objects.filter(is_active=True).order_by('name')
        service_types = TechnicalServiceType.objects.filter(is_active=True).order_by('name')
        return render(request, 'commercial/partials/edit_scope_item_modal.html', {
            'proposal': proposal,
            'item': item,
            'form': form,
            'disciplines': disciplines,
            'service_types': service_types,
        }, status=422)


class ProposalDeleteScopeItemView(LoginRequiredMixin, View):
    def post(self, request, pk, item_id):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        if proposal.status == ProposalStatusChoices.ACEITA:
            messages.error(request, _("Não é possível remover itens de uma proposta já aceita."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        item = get_object_or_404(ProposalScopeItem, pk=item_id, proposal=proposal)
        item.delete()
        messages.warning(request, _("Item de escopo removido da proposta."))
        return redirect('commercial:proposal_detail', pk=proposal.pk)


class ProposalAddInputRequirementView(LoginRequiredMixin, View):
    def post(self, request, pk):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        if proposal.status == ProposalStatusChoices.ACEITA:
            messages.error(request, _("Proposta já aceita. O checklist de insumos está travado. É necessário desbloqueá-la por alçada superior para realizar alterações."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        form = ProposalInputRequirementForm(request.POST)
        if form.is_valid():
            req_item = form.save(commit=False)
            req_item.proposal = proposal
            req_item.save()
            messages.success(request, _(f"Insumo '{req_item.get_required_item_type_display()}' adicionado ao checklist com sucesso."))
        else:
            err_msg = "; ".join([f"{f}: {e[0]}" for f, e in form.errors.items()])
            messages.error(request, _(f"Erro ao adicionar insumo: {err_msg}"))
        return redirect('commercial:proposal_detail', pk=proposal.pk)


class ProposalEditInputRequirementView(LoginRequiredMixin, View):
    """
    Permite modificar um insumo obrigatório do checklist da contratante (D0).
    """
    def get(self, request, pk, req_id):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        if proposal.status == ProposalStatusChoices.ACEITA:
            messages.error(request, _("Proposta já aceita. É necessário desbloqueá-la por alçada superior para alterar insumos."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        req_item = get_object_or_404(ProposalInputRequirement, pk=req_id, proposal=proposal)
        form = ProposalInputRequirementForm(instance=req_item)
        input_types = TechnicalInputType.objects.filter(is_active=True).order_by('category', 'name')
        return render(request, 'commercial/partials/edit_input_requirement_modal.html', {
            'proposal': proposal,
            'req_item': req_item,
            'form': form,
            'input_types': input_types,
        })

    def post(self, request, pk, req_id):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        if proposal.status == ProposalStatusChoices.ACEITA:
            messages.error(request, _("Proposta já aceita. É necessário desbloqueá-la por alçada superior para alterar insumos."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        req_item = get_object_or_404(ProposalInputRequirement, pk=req_id, proposal=proposal)
        form = ProposalInputRequirementForm(request.POST, instance=req_item)
        if form.is_valid():
            item = form.save(commit=True)
            messages.success(request, _(f"Insumo '{item.get_required_item_type_display()}' modificado com sucesso."))
            if request.headers.get('HX-Request'):
                response = HttpResponse("")
                response['HX-Refresh'] = 'true'
                return response
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        input_types = TechnicalInputType.objects.filter(is_active=True).order_by('category', 'name')
        return render(request, 'commercial/partials/edit_input_requirement_modal.html', {
            'proposal': proposal,
            'req_item': req_item,
            'form': form,
            'input_types': input_types,
        }, status=422)


class ProposalDeleteInputRequirementView(LoginRequiredMixin, View):
    """
    Permite remover um insumo obrigatório do checklist da contratante (D0).
    """
    def post(self, request, pk, req_id):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        if proposal.status == ProposalStatusChoices.ACEITA:
            messages.error(request, _("Não é possível remover insumos de uma proposta já aceita sem prévio desbloqueio."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        req_item = get_object_or_404(ProposalInputRequirement, pk=req_id, proposal=proposal)
        item_name = req_item.get_required_item_type_display()
        req_item.delete()
        messages.warning(request, _(f"Insumo '{item_name}' removido do checklist de responsabilidade do cliente."))
        return redirect('commercial:proposal_detail', pk=proposal.pk)

class ProposalValidateInputView(LoginRequiredMixin, View):
    """
    Homologação técnica de insumos pelo engenheiro geotécnico.
    """
    def get(self, request, pk, req_id):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        req_item = get_object_or_404(ProposalInputRequirement, pk=req_id, proposal=proposal)
        form = TechnicalInputValidationForm(instance=req_item)
        return render(request, 'commercial/partials/validate_input_modal.html', {
            'proposal': proposal,
            'req_item': req_item,
            'form': form
        })

    def post(self, request, pk, req_id):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        req_item = get_object_or_404(ProposalInputRequirement, pk=req_id, proposal=proposal)
        form = TechnicalInputValidationForm(request.POST, request.FILES, instance=req_item)
        if form.is_valid():
            item = form.save(commit=False)
            if item.status == InputStatusChoices.APROVADO:
                item.validated_by = request.user
                item.validated_at = timezone.now()
            item.save()
            messages.success(request, _(f"Insumo '{item.get_required_item_type_display()}' atualizado para {item.get_status_display()}."))
            response = HttpResponse("")
            response['HX-Refresh'] = 'true'
            return response
        return render(request, 'commercial/partials/validate_input_modal.html', {
            'proposal': proposal,
            'req_item': req_item,
            'form': form
        })

class ProposalSendView(LoginRequiredMixin, View):
    """
    Transiciona a proposta para ENVIADA e calcula a vigência final.
    """
    def post(self, request, pk):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        if proposal.scope_items.count() == 0:
            messages.error(request, _("A proposta não pode ser enviada sem pelo menos um item de escopo precificado."))
            return redirect('commercial:proposal_detail', pk=proposal.pk)

        proposal.status = ProposalStatusChoices.ENVIADA
        proposal.sent_at = timezone.now()
        proposal.expires_at = proposal.sent_at.date() + timedelta(days=proposal.validity_days)
        proposal.save()

        messages.success(
            request,
            _(f"Proposta {proposal.proposal_code} enviada formalmente! Válida até {proposal.expires_at:%d/%m/%Y}.")
        )
        return redirect('commercial:proposal_detail', pk=proposal.pk)

# ==============================================================================
# PORTAL PÚBLICO DE ACEITE ELETRÔNICO DO CLIENTE (LANDING PAGE COM TOKEN SEGURO)
# ==============================================================================

class ProposalPublicPortalView(View):
    """
    Landing page pública responsiva para visualização e aceite do cliente via HTTPS.
    """
    def get(self, request, token):
        proposal = get_object_or_404(CommercialProposal, public_token=token)
        accept_form = OnlineAcceptanceForm(initial={
            'signer_name': proposal.client.name if proposal.client.is_individual else '',
            'signer_doc': proposal.client.formatted_doc_number or proposal.client.doc_number
        })
        revision_form = ClientRevisionRequestForm()
        rejection_form = ClientRejectionForm()

        return render(request, 'commercial/public_proposal_portal.html', {
            'proposal': proposal,
            'scope_items': proposal.scope_items.all(),
            'input_requirements': proposal.input_requirements.all(),
            'accept_form': accept_form,
            'revision_form': revision_form,
            'rejection_form': rejection_form,
            'is_expired': proposal.is_expired(),
        })

class ProposalPublicActionView(View):
    """
    Processa Aceite Eletrônico, Solicitação de Revisão ou Recusa vindo da Landing Page.
    """
    def post(self, request, token):
        proposal = get_object_or_404(CommercialProposal, public_token=token)
        action = request.POST.get('action')
        ip_addr = get_client_ip(request) or '127.0.0.1'
        ua = request.META.get('HTTP_USER_AGENT', '')

        if action == 'accept':
            form = OnlineAcceptanceForm(request.POST)
            if form.is_valid():
                try:
                    proposal.accept_online(
                        signer_name=form.cleaned_data['signer_name'],
                        signer_doc=form.cleaned_data['signer_doc'],
                        signer_role=form.cleaned_data['signer_role'],
                        ip_address=ip_addr,
                        user_agent=ua
                    )
                    messages.success(request, _("Proposta aceita com sucesso! O contrato foi instanciado e nossa equipe de engenharia foi notificada."))
                except ValidationError as e:
                    messages.error(request, str(e.messages[0]))
            else:
                messages.error(request, _("Por favor, preencha todos os campos obrigatórios do aceite."))

        elif action == 'revision':
            form = ClientRevisionRequestForm(request.POST)
            if form.is_valid():
                proposal.status = ProposalStatusChoices.EM_REVISAO
                proposal.revision_notes = form.cleaned_data['revision_notes']
                proposal.save(update_fields=['status', 'revision_notes', 'updated_at'])
                messages.info(request, _("Sua solicitação de revisão foi enviada com sucesso para a equipe da Pangea Engenharia."))

        elif action == 'reject':
            form = ClientRejectionForm(request.POST)
            if form.is_valid():
                proposal.status = ProposalStatusChoices.DECLINADA
                proposal.rejection_reason = form.cleaned_data['rejection_reason']
                proposal.save(update_fields=['status', 'rejection_reason', 'updated_at'])
                messages.warning(request, _("Proposta comercial recusada."))

        return redirect('commercial:public_portal', token=token)

class ProposalPrintView(View):
    """
    Visualização para impressão / geração em PDF formal de proposta técnica.
    """
    def get(self, request, pk):
        proposal = get_object_or_404(CommercialProposal, pk=pk)
        return render(request, 'commercial/proposal_print.html', {
            'proposal': proposal,
            'scope_items': proposal.scope_items.all(),
            'input_requirements': proposal.input_requirements.all()
        })

# ==============================================================================
# GESTÃO CONTRATUAL E GATILHO DE MISE EN SERVICE (ENTRADA EM SERVIÇO)
# ==============================================================================

class ContractDetailView(LoginRequiredMixin, DetailView):
    model = LegalContract
    template_name = 'commercial/contract_detail.html'
    context_object_name = 'contract'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        can_start, pendencias = self.object.can_trigger_mise_en_service()
        context['can_start_mise_en_service'] = can_start
        context['mise_en_service_pendencias'] = pendencias
        context['contract_form'] = LegalContractForm(instance=self.object)
        return context

class ContractUpdateView(LoginRequiredMixin, UpdateView):
    model = LegalContract
    form_class = LegalContractForm
    template_name = 'commercial/contract_form.html'

    def form_valid(self, form):
        contract = form.save(commit=False)
        # Se anexou contrato assinado, atualiza status se ainda estiver em minuta
        if contract.signed_pdf and contract.status in (ContractStatusChoices.MINUTA, ContractStatusChoices.AGUARDANDO_ASSINATURA):
            contract.status = ContractStatusChoices.ASSINADO
            if not contract.signed_at:
                contract.signed_at = timezone.now().date()
        contract.save()
        messages.success(self.request, _("Minuta contratual atualizada com sucesso!"))
        return redirect('commercial:contract_detail', pk=contract.pk)

class ContractMiseEnServiceTriggerView(LoginRequiredMixin, View):
    """
    Gatilho que aciona o marco zero D0 e define a data final de entrega do projeto.
    """
    def post(self, request, pk):
        contract = get_object_or_404(LegalContract, pk=pk)
        try:
            d0, deadline = contract.trigger_mise_en_service(request.user)
            messages.success(
                request,
                _(f"Mise en Service acionado com sucesso! Marco Zero (D0) fixado em {d0:%d/%m/%Y}. "
                  f"Data Limite Final de Entrega: {deadline:%d/%m/%Y}.")
            )
        except ValidationError as e:
            messages.error(request, str(e.message_dict.get('status', [str(e)])[0]))

        return redirect('commercial:contract_detail', pk=contract.pk)

from apps.contacts.models import Contact

class ContactAutocompleteView(LoginRequiredMixin, View):
    """
    Endpoint JSON para busca preditiva rápida e sugestões automáticas de Clientes / Contratantes
    (Pessoas Jurídicas, SPEs, Filiais e Pessoas Físicas) com metadados estruturados.
    """
    def get(self, request):
        contact_id = request.GET.get('id', '').strip()
        if contact_id:
            c = Contact.objects.filter(pk=contact_id, is_active=True).select_related('parent').first()
            if not c:
                return JsonResponse({'found': False}, status=404)
            return JsonResponse({
                'found': True,
                'id': str(c.pk),
                'name': c.name,
                'trade_name': c.trade_name,
                'is_company': c.is_company,
                'type_display': c.get_contact_type_display(),
                'company_subtype': c.get_company_subtype_display() if c.is_company else '',
                'parent_name': c.parent.name if c.parent else '',
                'doc_number': c.formatted_doc_number,
                'city': c.city,
                'state': c.state,
                'location': f"{c.city}/{c.state}" if c.city and c.state else (c.city or c.state or ''),
                'avatar_url': c.avatar.url if c.avatar else None,
            })

        q = request.GET.get('q', '').strip()
        qs = Contact.objects.filter(is_active=True).select_related('parent').order_by('name')

        if q:
            clean_digits = ''.join(ch for ch in q if ch.isdigit())
            query = Q(name__icontains=q) | Q(trade_name__icontains=q) | Q(city__icontains=q) | Q(parent__name__icontains=q)
            if clean_digits:
                query |= Q(doc_number__icontains=clean_digits)
            qs = qs.filter(query)

        results = []
        for c in qs[:15]:
            results.append({
                'id': str(c.pk),
                'name': c.name,
                'trade_name': c.trade_name,
                'is_company': c.is_company,
                'type_display': c.get_contact_type_display(),
                'company_subtype': c.get_company_subtype_display() if c.is_company else '',
                'parent_name': c.parent.name if c.parent else '',
                'doc_number': c.formatted_doc_number,
                'location': f"{c.city}/{c.state}" if c.city and c.state else (c.city or c.state or ''),
                'avatar_url': c.avatar.url if c.avatar else None,
            })

        return JsonResponse({'results': results, 'total': len(results)})


class TechnicalInputAutocompleteView(LoginRequiredMixin, View):
    """
    Endpoint JSON de alta performance para busca preditiva on-the-fly de Insumos da Contratante.
    Permite filtrar por categoria (Técnico / Administrativo) e busca textual por termo.
    """
    def get(self, request):
        q = request.GET.get('q', '').strip()
        category = request.GET.get('category', '').strip().upper()

        qs = TechnicalInputType.objects.filter(is_active=True)

        if category and category in [c[0] for c in InputCategoryChoices.choices]:
            qs = qs.filter(category=category)

        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(code__icontains=q) |
                Q(default_description__icontains=q)
            )

        # Performance: limita aos primeiros 15 resultados
        results = []
        for inp in qs.order_by('category', 'name')[:15]:
            results.append({
                'id': str(inp.pk),
                'name': inp.name,
                'code': inp.code or '',
                'category': inp.category,
                'category_display': inp.get_category_display(),
                'default_description': inp.default_description or '',
                'is_mandatory_default': inp.is_mandatory_default,
            })

        exact_match = qs.filter(name__iexact=q).exists() if q else True

        return JsonResponse({
            'results': results,
            'total': len(results),
            'query': q,
            'exact_match': exact_match,
        })


class TechnicalInputQuickCreateView(LoginRequiredMixin, View):
    """
    Endpoint JSON para criação on-the-fly de novo insumo no catálogo após confirmação do usuário.
    Garante integridade, evita duplicatas e registra trilha de auditoria.
    """
    def post(self, request):
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body.decode('utf-8'))
            except Exception:
                data = {}
        else:
            data = request.POST

        name = data.get('name', '').strip()
        category = data.get('category', '').strip().upper()
        description = data.get('description', '').strip()
        is_mandatory_default = str(data.get('is_mandatory_default', 'true')).lower() in ['true', '1', 'on']

        if not name:
            return JsonResponse({'success': False, 'error': _('O nome do insumo não pode estar vazio.')}, status=400)

        if category not in [c[0] for c in InputCategoryChoices.choices]:
            category = InputCategoryChoices.TECNICO

        # Verifica se já existe com o mesmo nome (case-insensitive)
        existing = TechnicalInputType.objects.filter(name__iexact=name).first()
        if existing:
            return JsonResponse({
                'success': True,
                'created': False,
                'message': _('Insumo já cadastrado no catálogo corporativo.'),
                'input': {
                    'id': str(existing.pk),
                    'name': existing.name,
                    'code': existing.code or '',
                    'category': existing.category,
                    'category_display': existing.get_category_display(),
                    'default_description': existing.default_description or '',
                    'is_mandatory_default': existing.is_mandatory_default,
                }
            })

        # Cria novo código referencial se não fornecido
        prefix = 'TEC' if category == InputCategoryChoices.TECNICO else 'ADM'
        count = TechnicalInputType.objects.filter(category=category).count() + 1
        generated_code = f"{prefix}-AUTO-{count:02d}"

        new_input = TechnicalInputType.objects.create(
            name=name,
            code=generated_code,
            category=category,
            default_description=description or _('Fornecimento obrigatório pela contratante conforme normas técnicas.'),
            is_mandatory_default=is_mandatory_default,
            is_active=True
        )

        from apps.audit_log.models import AuditLog, AuditActionChoices
        AuditLog.objects.create(
            user=request.user,
            action=AuditActionChoices.CREATE,
            app_label='commercial',
            model_name='technicalinputtype',
            object_id=str(new_input.pk),
            object_repr=f"Criação On-The-Fly de Insumo: {new_input.name} ({new_input.category})",
            changes={
                'name': new_input.name,
                'category': new_input.category,
                'code': new_input.code,
                'created_by': getattr(request.user, 'email', str(request.user))
            }
        )

        return JsonResponse({
            'success': True,
            'created': True,
            'message': _('Novo insumo cadastrado com sucesso no catálogo corporativo.'),
            'input': {
                'id': str(new_input.pk),
                'name': new_input.name,
                'code': new_input.code,
                'category': new_input.category,
                'category_display': new_input.get_category_display(),
                'default_description': new_input.default_description,
                'is_mandatory_default': new_input.is_mandatory_default,
            }
        }, status=201)
