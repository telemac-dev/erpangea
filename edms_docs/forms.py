from django import forms
from .models import ProjectDocument, DocumentRevision, DocumentTypeEnum, RevisionStatusEnum

class DocumentCreateForm(forms.ModelForm):
    arquivo = forms.FileField(label="Arquivo Técnico (.dwg, .dxf, .pdf, .xlsx, .cype, etc.)")
    notas_alteracao = forms.CharField(label="Notas Iniciais", required=False, widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = ProjectDocument
        fields = ['projeto', 'tipo', 'codigo_identificador', 'titulo']

class RevisionUploadForm(forms.ModelForm):
    class Meta:
        model = DocumentRevision
        fields = ['arquivo', 'status', 'notas_alteracao']
        widgets = {
            'notas_alteracao': forms.Textarea(attrs={'rows': 3}),
        }
