import json
from decimal import Decimal
from datetime import date, timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
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
    ServiceTypeChoices,
    ContractTypeChoices
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
    paginate_by = 20

    def get_queryset(self):
        qs = CommercialProposal.objects.select_related('client', 'salesperson', 'technical_responsible')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(proposal_code__icontains=q) |
                Q(project_name__icontains=q) |
                Q(client__name__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['q'] = self.request.GET.get('q', '')
        context['statuses'] = ProposalStatusChoices.choices
        context['total_proposals'] = self.get_queryset().count()
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
        context['scope_items'] = self.object.scope_items.all()
        context['input_requirements'] = self.object.input_requirements.all()
        context['contract'] = getattr(self.object, 'contract', None)
        context['scope_form'] = ProposalScopeItemForm()
        context['input_form'] = ProposalInputRequirementForm()
        return context

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
            messages.error(request, _("Erro ao adicionar item de escopo. Verifique os campos."))
        return redirect('commercial:proposal_detail', pk=proposal.pk)

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
        form = ProposalInputRequirementForm(request.POST)
        if form.is_valid():
            req_item = form.save(commit=False)
            req_item.proposal = proposal
            req_item.save()
            messages.success(request, _("Insumo técnico adicionado ao checklist de responsabilidade do cliente."))
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
