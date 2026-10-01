from django import forms
from .models import Contact, PersonTypeEnum

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'tipo_pessoa', 'razao_social_nome', 'nome_fantasia', 
            'cpf_cnpj', 'inscricao_estadual', 'inscricao_municipal',
            'classificacoes', 'email_principal', 'telefone_principal'
        ]
