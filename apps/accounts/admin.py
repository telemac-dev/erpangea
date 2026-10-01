from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserSectorAssignment

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = _("Perfil e Habilitação Técnica")
    verbose_name_plural = _("Perfil e Habilitação Técnica")
    fields = ('job_title', 'crea_number', 'phone', 'avatar')

class UserSectorAssignmentInline(admin.TabularInline):
    model = UserSectorAssignment
    extra = 1
    fields = ('sector', 'level', 'is_primary')
    verbose_name = _("Atribuição de Setor e Alçada")
    verbose_name_plural = _("Atribuições de Setores e Alçadas (Multi-Setor)")

@admin.register(User)
class UserAdmin(BaseUserAdmin):
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
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'is_staff', 'is_active'),
        }),
    )

    @admin.display(description=_('Setores & Alçadas'))
    def get_sectors_badge(self, obj):
        assignments = obj.sector_assignments.all()
        if not assignments:
            return format_html('<span style="color: #999;">Sem setor</span>')
        
        badges = []
        for a in assignments:
            primary_style = "border: 1px solid #2563eb; font-weight: bold;" if a.is_primary else ""
            badges.append(
                f'<span style="background: #f1f5f9; padding: 3px 6px; border-radius: 4px; margin-right: 4px; font-size: 11px; {primary_style}">'
                f'{a.get_sector_display()} ({a.get_level_display()})'
                f'</span>'
            )
        return format_html("".join(badges))

    @admin.display(description=_('Status'))
    def get_lock_status(self, obj):
        return "🔒 Bloqueado" if obj.is_locked() else "✓ Ativo"
