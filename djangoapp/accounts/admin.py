from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, LoginHistory


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('profile',)
    
    def get_role(self, instance):
        return instance.profile.get_role_display()
    get_role.short_description = 'Função'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'phone', 'created_at')
    list_filter = ('role', 'department', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'department')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address')
    list_filter = ('login_time',)
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'login_time', 'ip_address', 'user_agent')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
