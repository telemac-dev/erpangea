from django import forms
from .models import Document, DocumentRevision

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'project', 'title', 'category', 'file', 'revision',
            'status', 'approved_by', 'notes'
        ]

class DocumentRevisionForm(forms.ModelForm):
    class Meta:
        model = DocumentRevision
        fields = ['revision_number', 'file', 'changes_summary']
