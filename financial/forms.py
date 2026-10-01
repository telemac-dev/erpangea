from django import forms
from .models import AccountPayable
from datetime import date

class AccountPayableForm(forms.ModelForm):
    class Meta:
        model = AccountPayable
        fields = [
            'fornecedor', 'projeto', 'centro_de_custo',
            'categoria_despesa', 'descricao', 'valor_nominal',
            'data_vencimento', 'comprovante_fiscal'
        ]
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
        }

class LiquidationForm(forms.ModelForm):
    class Meta:
        model = AccountPayable
        fields = ['data_pagamento', 'comprovante_pagamento']
        widgets = {
            'data_pagamento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_pagamento'].initial = date.today()
        self.fields['comprovante_pagamento'].required = True
