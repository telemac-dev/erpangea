from django import forms
from .models import MeasurementSheet

class MeasurementSheetForm(forms.ModelForm):
    class Meta:
        model = MeasurementSheet
        fields = ['contrato', 'competencia', 'valor_total_medido', 'documento_comprovatorio']
        widgets = {
            'competencia': forms.DateInput(attrs={'type': 'date'}),
        }
