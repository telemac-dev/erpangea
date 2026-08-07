from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.decorators import financial_required
from contacts.models import Contact
from .models import PayableBill, PaymentReceipt, BillStatusChoices, BillCategoryChoices
from .forms import PayableBillForm, PaymentReceiptForm

@financial_required
def bill_list(request):
    supplier_filter = request.GET.get('supplier', '')
    status_filter = request.GET.get('status', '')
    due_soon_filter = request.GET.get('due_soon', '')
    query = request.GET.get('q', '')

    today = timezone.now().date()
    next_week = today + timedelta(days=7)

    bills = PayableBill.objects.select_related('supplier', 'project', 'created_by').all()

    if query:
        bills = bills.filter(
            Q(bill_number__icontains=query) |
            Q(supplier__name__icontains=query) |
            Q(notes__icontains=query)
        )

    if supplier_filter:
        bills = bills.filter(supplier_id=supplier_filter)

    if status_filter:
        bills = bills.filter(status=status_filter)

    if due_soon_filter:
        bills = bills.filter(
            status__in=[BillStatusChoices.EM_ABERTO, BillStatusChoices.PARCIALMENTE_PAGO],
            due_date__gte=today,
            due_date__lte=next_week
        )

    # Aggregations for header summary
    total_open = bills.filter(status=BillStatusChoices.EM_ABERTO).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
    total_overdue = bills.filter(status=BillStatusChoices.EM_ABERTO, due_date__lt=today).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
    total_paid = bills.filter(status=BillStatusChoices.PAGO).aggregate(s=Sum('amount_paid'))['s'] or Decimal('0.00')

    suppliers = Contact.objects.filter(payable_bills__isnull=False).distinct()
    statuses = BillStatusChoices.choices

    context = {
        'bills': bills,
        'query': query,
        'supplier_filter': supplier_filter,
        'status_filter': status_filter,
        'due_soon_filter': due_soon_filter,
        'suppliers': suppliers,
        'statuses': statuses,
        'total_open': total_open,
        'total_overdue': total_overdue,
        'total_paid': total_paid,
    }
    return render(request, 'payables/bill_list.html', context)

@financial_required
def bill_create(request):
    if request.method == 'POST':
        form = PayableBillForm(request.POST, request.FILES)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.created_by = request.user
            bill.save()
            messages.success(request, f'Conta a pagar "{bill.bill_number}" cadastrada com sucesso!')
            return redirect('bill_detail', pk=bill.pk)
        else:
            messages.error(request, 'Erro ao cadastrar conta a pagar.')
    else:
        count = PayableBill.objects.count() + 1
        initial_number = f"DOC-2026-{count:03d}"
        form = PayableBillForm(initial={'bill_number': initial_number, 'issue_date': timezone.now().date()})

    return render(request, 'payables/bill_form.html', {'form': form, 'title': 'Nova Conta a Pagar'})

@financial_required
def bill_detail(request, pk):
    bill = get_object_or_404(
        PayableBill.objects.select_related('supplier', 'project', 'created_by')
        .prefetch_related('receipts__registered_by'),
        pk=pk
    )

    receipt_form = PaymentReceiptForm(initial={
        'payment_date': timezone.now().date(),
        'amount_paid': bill.amount - bill.amount_paid
    })

    if request.method == 'POST':
        receipt_form = PaymentReceiptForm(request.POST, request.FILES)
        if receipt_form.is_valid():
            receipt = receipt_form.save(commit=False)
            receipt.bill = bill
            receipt.registered_by = request.user
            receipt.save()

            # Update bill paid amount and status
            bill.amount_paid += receipt.amount_paid
            if bill.amount_paid >= bill.amount:
                bill.status = BillStatusChoices.PAGO
            else:
                bill.status = BillStatusChoices.PARCIALMENTE_PAGO
            bill.save()

            messages.success(request, f'Pagamento de R$ {receipt.amount_paid} registrado com sucesso!')
            return redirect('bill_detail', pk=bill.pk)
        else:
            messages.error(request, 'Erro ao registrar pagamento.')

    context = {
        'bill': bill,
        'receipts': bill.receipts.all(),
        'receipt_form': receipt_form,
    }
    return render(request, 'payables/bill_detail.html', context)

@financial_required
def bill_edit(request, pk):
    bill = get_object_or_404(PayableBill, pk=pk)
    if request.method == 'POST':
        form = PayableBillForm(request.POST, request.FILES, instance=bill)
        if form.is_valid():
            b = form.save()
            messages.success(request, f'Conta a pagar "{b.bill_number}" atualizada.')
            return redirect('bill_detail', pk=b.pk)
        else:
            messages.error(request, 'Erro ao atualizar conta.')
    else:
        form = PayableBillForm(instance=bill)

    return render(request, 'payables/bill_form.html', {'form': form, 'bill': bill, 'title': f'Editar Conta {bill.bill_number}'})

@financial_required
def payables_report(request):
    """Relatório gerencial de contas a pagar por fornecedor e categoria."""
    today = timezone.now().date()
    
    supplier_summary = PayableBill.objects.values('supplier__nome_razao_social').annotate(
        total_amount=Sum('amount'),
        total_paid=Sum('amount_paid'),
        total_open=Sum('amount', filter=Q(status=BillStatusChoices.EM_ABERTO)),
        count=Count('id')
    ).order_by('-total_amount')

    category_summary = PayableBill.objects.values('category').annotate(
        total_amount=Sum('amount'),
        count=Count('id')
    ).order_by('-total_amount')

    context = {
        'supplier_summary': supplier_summary,
        'category_summary': category_summary,
        'categories_dict': dict(BillCategoryChoices.choices),
        'today': today,
    }
    return render(request, 'payables/payables_report.html', context)
