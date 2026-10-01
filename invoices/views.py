from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import ServiceInvoice, AccountReceivable, InvoiceStatusEnum
from .forms import ServiceInvoiceForm
from measurements.models import MeasurementSheet

def invoice_list(request):
    invoices = ServiceInvoice.objects.all().select_related('medicao__contrato__proposta__cliente').order_by('-data_emissao')
    receivables = AccountReceivable.objects.all().select_related('nota_fiscal__medicao__contrato').order_by('data_vencimento')
    return render(request, 'invoices/list.html', {
        'invoices': invoices,
        'receivables': receivables
    })

def create_invoice_modal(request):
    error_msg = None
    initial_data = {}
    medicao_id = request.GET.get('medicao_id')
    if medicao_id:
        try:
            m = MeasurementSheet.objects.get(pk=medicao_id)
            initial_data['medicao'] = m
            initial_data['valor_bruto'] = m.valor_total_medido
        except MeasurementSheet.DoesNotExist:
            pass

    if request.method == 'POST':
        form = ServiceInvoiceForm(request.POST)
        if form.is_valid():
            try:
                invoice = form.save(commit=False)
                invoice.full_clean()
                invoice.save()
                response = HttpResponse('<div class="alert alert-success m-3">NFS-e emitida e contas a receber geradas!</div>')
                response['HX-Refresh'] = 'true'
                return response
            except ValidationError as e:
                error_msg = "; ".join(e.messages)
        else:
            error_msg = "Por favor, corrija os erros no formulário."
    else:
        form = ServiceInvoiceForm(initial=initial_data)

    return render(request, 'invoices/partials/create_invoice_modal.html', {
        'form': form,
        'error_msg': error_msg
    })

def cancel_invoice(request, pk):
    invoice = get_object_or_404(ServiceInvoice, pk=pk)
    if request.method == 'POST':
        invoice.cancel_invoice()
        response = HttpResponse('<div class="alert alert-warning m-3">NFS-e cancelada e medição estornada!</div>')
        response['HX-Refresh'] = 'true'
        return response
    return HttpResponse(status=405)
