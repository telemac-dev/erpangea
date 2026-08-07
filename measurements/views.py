from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Measurement, MeasurementStatusChoices
from .forms import MeasurementForm

@login_required
def measurement_list(request):
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')

    measurements = Measurement.objects.select_related('project', 'contract', 'measured_by', 'approved_by').all()

    if query:
        measurements = measurements.filter(
            Q(number__icontains=query) |
            Q(project__code__icontains=query) |
            Q(project__name__icontains=query) |
            Q(description__icontains=query)
        )

    if status_filter:
        measurements = measurements.filter(status=status_filter)

    statuses = MeasurementStatusChoices.choices

    context = {
        'measurements': measurements,
        'query': query,
        'status_filter': status_filter,
        'statuses': statuses,
    }
    return render(request, 'measurements/measurement_list.html', context)

@login_required
def measurement_create(request):
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.measured_by = request.user
            measurement.save()
            messages.success(request, f'Medição "{measurement.number}" criada com sucesso!')
            return redirect('measurement_detail', pk=measurement.pk)
        else:
            messages.error(request, 'Erro ao criar medição. Verifique os dados.')
    else:
        count = Measurement.objects.count() + 1
        initial_number = f"MED-2026-{count:03d}"
        form = MeasurementForm(initial={'number': initial_number})

    return render(request, 'measurements/measurement_form.html', {'form': form, 'title': 'Nova Medição de Obra'})

@login_required
def measurement_detail(request, pk):
    measurement = get_object_or_404(
        Measurement.objects.select_related('project__client', 'contract', 'measured_by', 'approved_by'),
        pk=pk
    )
    return render(request, 'measurements/measurement_detail.html', {'measurement': measurement})

@login_required
def measurement_approve(request, pk):
    measurement = get_object_or_404(Measurement, pk=pk)
    if request.method == 'POST':
        measurement.status = MeasurementStatusChoices.APROVADA
        measurement.approved_by = request.user
        measurement.approval_date = timezone.now()
        measurement.save()
        messages.success(request, f'Medição "{measurement.number}" aprovada com sucesso!')
    return redirect('measurement_detail', pk=measurement.pk)

@login_required
def measurement_edit(request, pk):
    measurement = get_object_or_404(Measurement, pk=pk)
    if request.method == 'POST':
        form = MeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            m = form.save()
            messages.success(request, f'Medição "{m.number}" atualizada.')
            return redirect('measurement_detail', pk=m.pk)
        else:
            messages.error(request, 'Erro ao atualizar medição.')
    else:
        form = MeasurementForm(instance=measurement)

    return render(request, 'measurements/measurement_form.html', {'form': form, 'measurement': measurement, 'title': f'Editar Medição {measurement.number}'})
