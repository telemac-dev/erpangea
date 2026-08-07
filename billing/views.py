from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from accounts.decorators import financial_required
from .models import Invoice, InvoiceStatusChoices
from .forms import InvoiceForm

@financial_required
def invoice_list(request):
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')

    invoices = Invoice.objects.select_related('client', 'contract', 'measurement').all()

    if query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=query) |
            Q(client__name__icontains=query) |
            Q(notes__icontains=query)
        )

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    statuses = InvoiceStatusChoices.choices

    context = {
        'invoices': invoices,
        'query': query,
        'status_filter': status_filter,
        'statuses': statuses,
    }
    return render(request, 'billing/invoice_list.html', context)

@financial_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Fatura / NF "{invoice.invoice_number}" registrada com sucesso!')
            return redirect('invoice_detail', pk=invoice.pk)
        else:
            messages.error(request, 'Erro ao registrar fatura.')
    else:
        count = Invoice.objects.count() + 1
        initial_number = f"NF-2026-{count:03d}"
        form = InvoiceForm(initial={'invoice_number': initial_number, 'issue_date': timezone.now().date()})

    return render(request, 'billing/invoice_form.html', {'form': form, 'title': 'Nova Fatura / Nota Fiscal'})

@financial_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('client', 'contract', 'measurement__project'),
        pk=pk
    )
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})

@financial_required
def invoice_register_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.status = InvoiceStatusChoices.PAGO
        invoice.payment_date = timezone.now().date()
        invoice.amount_paid = invoice.amount
        invoice.save()
        messages.success(request, f'Pagamento da fatura "{invoice.invoice_number}" registrado com sucesso!')
    return redirect('invoice_detail', pk=invoice.pk)

@financial_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            inv = form.save()
            messages.success(request, f'Fatura "{inv.invoice_number}" atualizada.')
            return redirect('invoice_detail', pk=inv.pk)
        else:
            messages.error(request, 'Erro ao atualizar fatura.')
    else:
        form = InvoiceForm(instance=invoice)

    return render(request, 'billing/invoice_form.html', {'form': form, 'invoice': invoice, 'title': f'Editar Fatura {invoice.invoice_number}'})
