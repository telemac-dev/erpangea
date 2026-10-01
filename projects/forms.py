from django import forms
from .models import Task, ProjectPhase, Project

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['fase', 'titulo', 'responsavel', 'prioridade', 'horas_previstas']

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields['fase'].queryset = ProjectPhase.objects.filter(projeto=project)
