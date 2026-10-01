from django import forms
from .models import ServiceInvoice
from measurements.models import MeasurementSheet, MeasurementStatusEnum

class ServiceInvoiceForm(forms.ModelForm):
    class Meta:
        model = ServiceInvoice
        fields = ['medicao', 'numero_nfse', 'codigo_verificacao', 'data_emissao', 'valor_bruto', 'aliquota_iss']
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas medições aprovadas pelo cliente
        self.fields['medicao'].queryset = MeasurementSheet.objects.filter(
            status=MeasurementStatusEnum.APROVADA_CLIENTE
        )
