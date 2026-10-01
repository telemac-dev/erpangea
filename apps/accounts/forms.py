import re
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile
from .templatetags.phone_filters import format_phone_br

class UserAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("E-mail Corporativo"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg border-start-0',
            'placeholder': 'nome@pangea.com.br',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_("Senha de Acesso"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg border-start-0 border-end-0',
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
                'placeholder': '(11) 9 9876-5432',
                'maxlength': '20',
                'id': 'id_phone',
                'autocomplete': 'tel'
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
            if self.instance.phone:
                self.fields['phone'].initial = format_phone_br(self.instance.phone)

    def clean_phone(self):
        raw_phone = self.cleaned_data.get('phone', '')
        if not raw_phone:
            return ""
        
        digits = re.sub(r'\D', '', str(raw_phone))
        
        # Validacao da quantidade de digitos para telefones brasileiros (10 ou 11)
        if len(digits) not in (10, 11):
            raise ValidationError(
                _("Número de telefone inválido. Informe o DDD seguido de 8 ou 9 dígitos (ex: (11) 9 9876-5432).")
            )
            
        # Formata padronizado para salvar no banco
        return format_phone_br(digits)

    def save(self, commit=True):
        profile = super().save(commit=commit)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save(update_fields=['first_name', 'last_name'])
        return profile

class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control border-start-0 border-end-0',
                'placeholder': '••••••••'
            })
        self.fields['old_password'].label = _("Senha Atual")
        self.fields['new_password1'].label = _("Nova Senha")
        self.fields['new_password2'].label = _("Confirmação da Nova Senha")

class UserPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'seu-email@pangea.com.br',
            'autofocus': True
        })
        self.fields['email'].label = _("E-mail Corporativo Cadastrado")

class UserSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-lg border-start-0 border-end-0',
                'placeholder': '••••••••'
            })
        self.fields['new_password1'].label = _("Nova Senha")
        self.fields['new_password2'].label = _("Confirmar Nova Senha")
