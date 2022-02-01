from django import forms
from pessoa.models import Pessoa, Telefone, Endereco


class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = '__all__'
        
        
class TelefoneForm(forms.ModelForm):
    class Meta:
        model = Telefone
        fields = '__all__'
        

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = '__all__'