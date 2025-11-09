from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class LoginForm(AuthenticationForm):
    """
    Formulário customizado de login
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Digite seu usuário ou email',
            'autofocus': True
        }),
        label='Usuário ou Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Digite sua senha'
        }),
        label='Senha'
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Lembrar-me'
    )


class UserRegisterForm(UserCreationForm):
    """
    Formulário de registro de novo usuário
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        }),
        label='Nome'
    )
    last_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        }),
        label='Sobrenome'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Escolha um nome de usuário'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Crie uma senha forte'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme sua senha'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado.')
        return email


class UserUpdateForm(forms.ModelForm):
    """
    Formulário para atualizar informações do usuário
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """
    Formulário para atualizar o perfil do usuário
    """
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'role', 'phone', 'department', 
            'bio', 'birth_date', 'address', 'city', 
            'state', 'zip_code'
        ]
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Vendas, TI, RH'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Conte um pouco sobre você...'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua, número, complemento'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UF',
                'maxlength': '2'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000'
            }),
        }
