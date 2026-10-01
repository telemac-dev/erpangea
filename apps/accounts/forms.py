from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile

class UserAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("E-mail Corporativo"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'nome@pangea.com.br',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_("Senha de Acesso"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '••••••••'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        if email:
            user = User.objects.filter(email=email).first()
            if user and user.is_locked():
                raise ValidationError(
                    _("Conta temporariamente bloqueada devido a sucessivas tentativas com falha. "
                      "Aguarde alguns minutos antes de tentar novamente."),
                    code='account_locked'
                )
        return super().clean()

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        label=_("Primeiro Nome"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Carlos'
        })
    )
    last_name = forms.CharField(
        label=_("Sobrenome"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Silva'
        })
    )

    class Meta:
        model = UserProfile
        fields = ['phone', 'job_title', 'crea_number', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 98765-4321',
                'maxlength': '20'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Engenheiro Geotécnico Sênior'
            }),
            'crea_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CREA-SP 5061234567/D'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'phone': _('Telefone Corporativo'),
            'job_title': _('Cargo / Especialidade'),
            'crea_number': _('Registro CREA / UF'),
            'avatar': _('Foto de Identificação'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=commit)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save(update_fields=['first_name', 'last_name'])
        return profile
