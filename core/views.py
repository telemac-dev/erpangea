from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from commercial.models import Lead, Proposal, Contract, ProposalStatusChoices, ContractStatusChoices, LeadStageChoices
from projects.models import Project, Task, Delivery, ProjectStatusChoices, TaskStatusChoices, DeliveryStatusChoices
from measurements.models import Measurement, MeasurementStatusChoices
from billing.models import Invoice, InvoiceStatusChoices
from payables.models import PayableBill, BillStatusChoices
from contacts.models import Contact

@login_required
def home(request):
    today = timezone.now().date()
    next_week = today + timedelta(days=7)

    # 1. Commercial Indicators
    total_leads = Lead.objects.exclude(stage=LeadStageChoices.PERDIDO).count()
    pipeline_value = Lead.objects.exclude(stage=LeadStageChoices.PERDIDO).aggregate(val=Sum('estimated_value'))['val'] or Decimal('0.00')
    active_proposals_count = Proposal.objects.filter(status__in=[ProposalStatusChoices.ENVIADA, ProposalStatusChoices.EM_NEGOCIACAO, ProposalStatusChoices.APROVADA]).count()
    active_contracts_count = Contract.objects.filter(status__in=[ContractStatusChoices.ASSINADO, ContractStatusChoices.ATIVO]).count()

    # 2. Operational Indicators
    total_projects = Project.objects.count()
    ongoing_projects_count = Project.objects.filter(status=ProjectStatusChoices.EM_ANDAMENTO).count()
    delayed_projects_count = Project.objects.exclude(status=ProjectStatusChoices.CONCLUIDO).filter(expected_completion_date__lt=today).count()
    pending_tasks_count = Task.objects.filter(status__in=[TaskStatusChoices.PENDENTE, TaskStatusChoices.EM_ANDAMENTO]).count()
    pending_deliveries_count = Delivery.objects.filter(status=DeliveryStatusChoices.AGUARDANDO_APROVACAO).count()

    # 3. Financial Indicators - Receivables (Contas a Receber) & Contacts
    total_contacts = Contact.objects.count()
    total_invoiced = Invoice.objects.filter(status=InvoiceStatusChoices.PAGO).aggregate(val=Sum('amount'))['val'] or Decimal('0.00')
    pending_receivables = Invoice.objects.filter(status=InvoiceStatusChoices.EM_ABERTO).aggregate(val=Sum('amount'))['val'] or Decimal('0.00')
    overdue_receivables = Invoice.objects.filter(status=InvoiceStatusChoices.EM_ABERTO, due_date__lt=today).aggregate(val=Sum('amount'))['val'] or Decimal('0.00')
    approved_unbilled_measurements = Measurement.objects.filter(status=MeasurementStatusChoices.APROVADA).aggregate(val=Sum('measured_value'))['val'] or Decimal('0.00')

    # 4. Financial Indicators - Payables (Contas a Pagar / Despesas de Fornecedores)
    payables_open = PayableBill.objects.filter(status=BillStatusChoices.EM_ABERTO).aggregate(val=Sum('amount'))['val'] or Decimal('0.00')
    payables_overdue = PayableBill.objects.filter(status=BillStatusChoices.EM_ABERTO, due_date__lt=today).aggregate(val=Sum('amount'))['val'] or Decimal('0.00')
    payables_due_soon_count = PayableBill.objects.filter(status=BillStatusChoices.EM_ABERTO, due_date__gte=today, due_date__lte=next_week).count()
    payables_paid = PayableBill.objects.filter(status=BillStatusChoices.PAGO).aggregate(val=Sum('amount_paid'))['val'] or Decimal('0.00')

    context = {
        # Commercial
        'total_leads': total_leads,
        'pipeline_value': pipeline_value,
        'active_proposals_count': active_proposals_count,
        'active_contracts_count': active_contracts_count,
        
        # Operational
        'total_projects': total_projects,
        'ongoing_projects_count': ongoing_projects_count,
        'delayed_projects_count': delayed_projects_count,
        'pending_tasks_count': pending_tasks_count,
        'pending_deliveries_count': pending_deliveries_count,
        
        # Financial Receivables & Contacts
        'total_contacts': total_contacts,
        'total_invoiced': total_invoiced,
        'pending_receivables': pending_receivables,
        'overdue_receivables': overdue_receivables,
        'approved_unbilled_measurements': approved_unbilled_measurements,

        # Financial Payables (Contas a Pagar)
        'payables_open': payables_open,
        'payables_overdue': payables_overdue,
        'payables_due_soon_count': payables_due_soon_count,
        'payables_paid': payables_paid,
    }
    return render(request, 'home.html', context)
