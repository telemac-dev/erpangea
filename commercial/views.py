from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Proposal, ProposalStatusEnum
from .forms import ProposalForm

def proposal_list(request):
    proposals = Proposal.objects.all().order_by('-id')
    return render(request, 'commercial/proposals_list.html', {'proposals': proposals})

def create_proposal_modal(request):
    form = ProposalForm()
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse('Criado com sucesso.')
            response['HX-Refresh'] = 'true'
            return response
            
    return render(request, 'commercial/partials/create_proposal_modal.html', {'form': form})

def approve_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    if request.method == 'POST':
        try:
            proposal.status = ProposalStatusEnum.APROVADA
            proposal.save() # Isso dispara o signal que cria o Contrato
            return HttpResponse(f'<span class="badge bg-success">Aprovada (Contrato Gerado)</span>')
        except Exception as e:
            return HttpResponse(f'<div class="text-danger">Erro: {str(e)}</div>')
            
    # Se for GET, retorna modal de confirmação
    return render(request, 'commercial/partials/approve_modal.html', {'proposal': proposal})
