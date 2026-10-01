from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import MeasurementSheet, MeasurementStatusEnum
from .forms import MeasurementSheetForm

def measurement_list(request):
    measurements = MeasurementSheet.objects.all().select_related('contrato__proposta__cliente').order_by('-id')
    return render(request, 'measurements/list.html', {'measurements': measurements})

def create_measurement_modal(request):
    error_msg = None
    if request.method == 'POST':
        form = MeasurementSheetForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                sheet = form.save(commit=False)
                sheet.full_clean()
                sheet.save()
                response = HttpResponse('<div class="alert alert-success m-3">Medição registrada com sucesso!</div>')
                response['HX-Refresh'] = 'true'
                return response
            except ValidationError as e:
                error_msg = "; ".join(e.messages)
        else:
            error_msg = "Por favor, corrija os erros no formulário."
    else:
        form = MeasurementSheetForm()
        
    return render(request, 'measurements/partials/create_measurement_modal.html', {
        'form': form,
        'error_msg': error_msg
    })

def approve_measurement(request, pk):
    sheet = get_object_or_404(MeasurementSheet, pk=pk)
    if request.method == 'POST':
        sheet.status = MeasurementStatusEnum.APROVADA_CLIENTE
        sheet.save()
        response = HttpResponse('<span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25"><i class="bi bi-check-circle me-1"></i>Aprovada pelo Cliente</span>')
        return response
    return HttpResponse(status=405)
