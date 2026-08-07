from django import forms
from .models import Project, Task, Delivery

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'code', 'name', 'client', 'contract', 'service_type', 'description',
            'technical_responsible', 'manager', 'site_address', 'city', 'state',
            'start_date', 'expected_completion_date', 'actual_completion_date', 'status'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_completion_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_completion_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['title', 'description', 'delivery_date', 'status', 'notes']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }
