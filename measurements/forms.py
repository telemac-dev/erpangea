from django import forms
from .models import Measurement

class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = [
            'project', 'contract', 'number', 'measurement_date',
            'period_start', 'period_end', 'measured_value',
            'percentage_completed', 'description', 'status',
            'approved_by'
        ]
        widgets = {
            'measurement_date': forms.DateInput(attrs={'type': 'date'}),
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
        }
