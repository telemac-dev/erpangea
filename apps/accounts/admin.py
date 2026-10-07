from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserSectorAssignment


class UserAdminCreationForm(forms.ModelForm):
    """
    Formulário para cadastro de novos usuários no Django Admin com hashing criptográfico de senha.
    """
    password1 = forms.CharField(
        label=_("Senha"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        strip=False,
        help_text=_("A senha deve conter no mínimo 8 caracteres.")
    )
    password2 = forms.CharField(
        label=_("Confirmação de Senha"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        strip=False,
        help_text=_("Digite a mesma senha novamente para confirmação.")
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_superuser')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Já existe um colaborador cadastrado com este e-mail."))
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_("As senhas digitadas não coincidem."))
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """
    Formulário para edição de usuários existentes com exibição segura de hash de senha.
    """
    password = ReadOnlyPasswordHashField(
        label=_("Senha"),
        help_text=_(
            "As senhas são armazenadas criptografadas irreversivelmente (hash). "
            "Para alterar a senha do usuário, utilize a interface de redefinição de credenciais."
        )
    )

    class Meta:
        model = User
        fields = '__all__'


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = _("Perfil e Habilitação Técnica")
    verbose_name_plural = _("Perfil e Habilitação Técnica")
    fields = ('job_title', 'crea_number', 'phone', 'avatar')


class UserSectorAssignmentInline(admin.TabularInline):
    model = UserSectorAssignment
    extra = 0
    fields = ('sector', 'level', 'is_primary')
    verbose_name = _("Atribuição de Setor e Alçada")
    verbose_name_plural = _("Atribuições de Setores e Alçadas (Multi-Setor)")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserAdminCreationForm
    form = UserAdminChangeForm
    inlines = (UserProfileInline, UserSectorAssignmentInline)
    list_display = (
        'email',
        'first_name',
        'last_name',
        'get_sectors_badge',
        'is_staff',
        'is_active',
        'get_lock_status',
        'date_joined'
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'sector_assignments__sector',
        'sector_assignments__level'
    )
    search_fields = (
        'email',
        'first_name',
        'last_name',
        'profile__crea_number',
        'profile__job_title'
    )
    ordering = ('-date_joined',)

    fieldsets = (
        (_('Credenciais de Acesso'), {'fields': ('email', 'password')}),
        (_('Identificação Pessoal'), {'fields': ('first_name', 'last_name')}),
        (_('Permissões e Acessos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Governança e Segurança'), {
            'fields': ('failed_login_attempts', 'locked_until'),
            'classes': ('collapse',),
        }),
        (_('Histórico de Sessão'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (_('Credenciais de Acesso'), {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        (_('Identificação Pessoal'), {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name'),
        }),
        (_('Permissões Básicas'), {
            'classes': ('wide',),
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )

    def get_inlines(self, request, obj=None):
        if not obj:
            # Na tela de criação de novo usuário, não renderiza inlines para evitar conflito com signals
            return ()
        return super().get_inlines(request, obj)

    @admin.display(description=_('Setores & Alçadas'))
    def get_sectors_badge(self, obj):
        assignments = obj.sector_assignments.all()
        if not assignments:
            return mark_safe('<span style="color: #94a3b8; font-size: 11px;">Sem setor</span>')
        
        badges = []
        for a in assignments:
            if a.is_primary:
                style = "border: 1px solid #2563eb; color: #1e40af; background: #eff6ff; font-weight: 600;"
                star = " ★"
            else:
                style = "border: 1px solid #e2e8f0; color: #334155; background: #f8fafc;"
                star = ""
            badges.append(
                f'<span style="{style} padding: 2px 6px; border-radius: 4px; margin-right: 4px; font-size: 11px; display: inline-block;">'
                f'{a.get_sector_display()} ({a.get_level_display()}){star}'
                f'</span>'
            )
        return mark_safe(" ".join(badges))

    @admin.display(description=_('Status'))
    def get_lock_status(self, obj):
        return "🔒 Bloqueado" if obj.is_locked() else "✓ Ativo"
