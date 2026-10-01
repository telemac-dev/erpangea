from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal
from .models import AccountPayable, PayableStatusEnum
from .forms import AccountPayableForm, LiquidationForm
from projects.models import Project
from measurements.models import MeasurementSheet, MeasurementStatusEnum

def payable_list(request):
    payables = AccountPayable.objects.all().select_related('fornecedor', 'projeto').order_by('data_vencimento')
    
    total_aguardando = payables.filter(status=PayableStatusEnum.AGUARDANDO_APROVACAO).aggregate(s=Sum('valor_nominal'))['s'] or Decimal('0.00')
    total_aprovado = payables.filter(status=PayableStatusEnum.APROVADA).aggregate(s=Sum('valor_nominal'))['s'] or Decimal('0.00')
    total_liquidado = payables.filter(status=PayableStatusEnum.LIQUIDADA).aggregate(s=Sum('valor_nominal'))['s'] or Decimal('0.00')
    
    projects = Project.objects.all()

    return render(request, 'financial/list.html', {
        'payables': payables,
        'total_aguardando': total_aguardando,
        'total_aprovado': total_aprovado,
        'total_liquidado': total_liquidado,
        'projects': projects,
    })

def create_payable_modal(request):
    error_msg = None
    if request.method == 'POST':
        form = AccountPayableForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                payable = form.save(commit=False)
                payable.criado_por = request.user
                payable.full_clean()
                payable.save()
                response = HttpResponse('<div class="alert alert-success m-3">Despesa lançada com sucesso!</div>')
                response['HX-Refresh'] = 'true'
                return response
            except ValidationError as e:
                error_msg = "; ".join(e.messages)
        else:
            error_msg = "Por favor, corrija os erros no formulário."
    else:
        form = AccountPayableForm()

    return render(request, 'financial/partials/create_payable_modal.html', {
        'form': form,
        'error_msg': error_msg
    })

def approve_payable(request, pk):
    payable = get_object_or_404(AccountPayable, pk=pk)
    if request.method == 'POST':
        payable.status = PayableStatusEnum.APROVADA
        payable.save()
        response = HttpResponse('<span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25"><i class="bi bi-check-circle me-1"></i>Aprovada</span>')
        return response
    return HttpResponse(status=405)

def liquidate_payable_modal(request, pk):
    payable = get_object_or_404(AccountPayable, pk=pk)
    error_msg = None
    if request.method == 'POST':
        form = LiquidationForm(request.POST, request.FILES, instance=payable)
        if form.is_valid():
            try:
                liq = form.save(commit=False)
                liq.status = PayableStatusEnum.LIQUIDADA
                liq.full_clean()
                liq.save()
                response = HttpResponse('<div class="alert alert-success m-3">Despesa liquidada com sucesso!</div>')
                response['HX-Refresh'] = 'true'
                return response
            except ValidationError as e:
                error_msg = "; ".join(e.messages)
        else:
            error_msg = "É obrigatório anexar o comprovante bancário."
    else:
        form = LiquidationForm(instance=payable)

    return render(request, 'financial/partials/liquidate_modal.html', {
        'payable': payable,
        'form': form,
        'error_msg': error_msg
    })

def project_profitability_report(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Receitas apuradas (Medições do contrato vinculado ao projeto)
    contract = getattr(project.ordem_servico, 'contrato', None)
    if contract:
        receita_medida = MeasurementSheet.objects.filter(
            contrato=contract
        ).exclude(status=MeasurementStatusEnum.REJEITADA).aggregate(s=Sum('valor_total_medido'))['s'] or Decimal('0.00')
    else:
        receita_medida = Decimal('0.00')

    # Despesas diretamente alocadas ao projeto
    despesas_projeto = AccountPayable.objects.filter(
        projeto=project
    ).exclude(status=PayableStatusEnum.CANCELADA)
    
    total_despesas = despesas_projeto.aggregate(s=Sum('valor_nominal'))['s'] or Decimal('0.00')
    margem_direta = receita_medida - total_despesas
    margem_percentual = ((margem_direta / receita_medida) * 100) if receita_medida > 0 else Decimal('0.00')

    return render(request, 'financial/project_report.html', {
        'project': project,
        'contract': contract,
        'receita_medida': receita_medida,
        'despesas_projeto': despesas_projeto,
        'total_despesas': total_despesas,
        'margem_direta': margem_direta,
        'margem_percentual': margem_percentual,
    })
