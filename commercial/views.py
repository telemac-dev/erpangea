from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Lead, Proposal, Contract, LeadStageChoices, ProposalStatusChoices, ContractStatusChoices
from .forms import LeadForm, ProposalForm, ContractForm

# --- LEADS / OPPORTUNITIES ---

@login_required
def lead_list(request):
    stage_filter = request.GET.get('stage', '')
    query = request.GET.get('q', '')

    leads = Lead.objects.select_related('contact', 'assigned_to').all()

    if query:
        leads = leads.filter(
            Q(contact__name__icontains=query) |
            Q(description__icontains=query) |
            Q(source__icontains=query)
        )

    if stage_filter:
        leads = leads.filter(stage=stage_filter)

    stages = LeadStageChoices.choices

    context = {
        'leads': leads,
        'query': query,
        'stage_filter': stage_filter,
        'stages': stages,
    }
    return render(request, 'commercial/lead_list.html', context)

@login_required
def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            messages.success(request, f'Lead para "{lead.contact.name}" criado com sucesso!')
            return redirect('lead_list')
        else:
            messages.error(request, 'Erro ao cadastrar lead.')
    else:
        form = LeadForm()

    return render(request, 'commercial/lead_form.html', {'form': form, 'title': 'Novo Lead / Oportunidade'})

@login_required
def lead_edit(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            lead = form.save()
            messages.success(request, f'Lead de "{lead.contact.name}" atualizado.')
            return redirect('lead_list')
        else:
            messages.error(request, 'Erro ao atualizar lead.')
    else:
        form = LeadForm(instance=lead)

    return render(request, 'commercial/lead_form.html', {'form': form, 'title': f'Editar Lead #{lead.pk}'})


# --- PROPOSALS (WITH HISTORICAL VERSIONING) ---

@login_required
def proposal_list(request):
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')

    proposals = Proposal.objects.select_related('client', 'technical_responsible', 'commercial_responsible').all()

    if query:
        proposals = proposals.filter(
            Q(number__icontains=query) |
            Q(client__name__icontains=query) |
            Q(scope__icontains=query)
        )

    if status_filter:
        proposals = proposals.filter(status=status_filter)

    statuses = ProposalStatusChoices.choices

    context = {
        'proposals': proposals,
        'query': query,
        'status_filter': status_filter,
        'statuses': statuses,
    }
    return render(request, 'commercial/proposal_list.html', context)

@login_required
def proposal_create(request):
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save()
            messages.success(request, f'Proposta "{proposal.number}" v{proposal.version} criada com sucesso!')
            return redirect('proposal_detail', pk=proposal.pk)
        else:
            messages.error(request, 'Erro ao cadastrar proposta.')
    else:
        # Generate initial proposal number example PROP-2026-001
        count = Proposal.objects.count() + 1
        initial_number = f"PROP-2026-{count:03d}"
        form = ProposalForm(initial={'number': initial_number, 'version': 1})

    return render(request, 'commercial/proposal_form.html', {'form': form, 'title': 'Nova Proposta Técnica'})

@login_required
def proposal_detail(request, pk):
    proposal = get_object_or_404(
        Proposal.objects.select_related(
            'client', 'lead', 'parent_proposal', 'technical_responsible', 'commercial_responsible'
        ).prefetch_related('previous_versions'), 
        pk=pk
    )
    return render(request, 'commercial/proposal_detail.html', {'proposal': proposal})

@login_required
def proposal_create_new_version(request, pk):
    """Requisito 573: Versionamento de propostas - Cria uma nova versão preservando o histórico."""
    old_proposal = get_object_or_404(Proposal, pk=pk)
    
    # Duplicate as a new version
    new_version_num = old_proposal.version + 1
    new_proposal = Proposal.objects.create(
        number=old_proposal.number,
        version=new_version_num,
        parent_proposal=old_proposal,
        client=old_proposal.client,
        lead=old_proposal.lead,
        scope=old_proposal.scope,
        included_services=old_proposal.included_services,
        exclusions=old_proposal.exclusions,
        assumptions=old_proposal.assumptions,
        execution_period_days=old_proposal.execution_period_days,
        validity_days=old_proposal.validity_days,
        total_value=old_proposal.total_value,
        payment_terms=old_proposal.payment_terms,
        technical_responsible=old_proposal.technical_responsible,
        commercial_responsible=old_proposal.commercial_responsible,
        status=ProposalStatusChoices.EM_REVISAO
    )
    messages.success(request, f'Nova versão v{new_proposal.version} criada para a proposta {new_proposal.number}.')
    return redirect('proposal_edit', pk=new_proposal.pk)

@login_required
def proposal_edit(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    if request.method == 'POST':
        form = ProposalForm(request.POST, instance=proposal)
        if form.is_valid():
            proposal = form.save()
            messages.success(request, f'Proposta "{proposal.number}" v{proposal.version} atualizada.')
            return redirect('proposal_detail', pk=proposal.pk)
        else:
            messages.error(request, 'Erro ao atualizar proposta.')
    else:
        form = ProposalForm(instance=proposal)

    return render(request, 'commercial/proposal_form.html', {'form': form, 'proposal': proposal, 'title': f'Editar Proposta {proposal.number} v{proposal.version}'})


# --- CONTRACTS ---

@login_required
def contract_list(request):
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')

    contracts = Contract.objects.select_related('client', 'proposal', 'responsible').all()

    if query:
        contracts = contracts.filter(
            Q(number__icontains=query) |
            Q(client__name__icontains=query)
        )

    if status_filter:
        contracts = contracts.filter(status=status_filter)

    statuses = ContractStatusChoices.choices

    context = {
        'contracts': contracts,
        'query': query,
        'status_filter': status_filter,
        'statuses': statuses,
    }
    return render(request, 'commercial/contract_list.html', context)

@login_required
def contract_create(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save()
            messages.success(request, f'Contrato "{contract.number}" registrado com sucesso!')
            return redirect('contract_list')
        else:
            messages.error(request, 'Erro ao registrar contrato.')
    else:
        count = Contract.objects.count() + 1
        initial_number = f"CONT-2026-{count:03d}"
        form = ContractForm(initial={'number': initial_number})

    return render(request, 'commercial/contract_form.html', {'form': form, 'title': 'Novo Contrato'})
