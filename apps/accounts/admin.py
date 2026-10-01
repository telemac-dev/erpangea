from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = _("Perfil e Habilitação Técnica")
    verbose_name_plural = _("Perfil e Habilitação Técnica")
    fields = ('sector', 'job_title', 'crea_number', 'phone', 'avatar')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    list_display = (
        'email',
        'first_name',
        'last_name',
        'get_sector',
        'is_staff',
        'is_active',
        'get_lock_status',
        'date_joined'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__sector')
    search_fields = ('email', 'first_name', 'last_name', 'profile__crea_number', 'profile__job_title')
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
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'is_staff', 'is_active'),
        }),
    )

    @admin.display(description=_('Setor'))
    def get_sector(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.get_sector_display() if profile else '-'

    @admin.display(description=_('Bloqueio'))
    def get_lock_status(self, obj):
        return "🔒 Bloqueado" if obj.is_locked() else "✓ Normal"
