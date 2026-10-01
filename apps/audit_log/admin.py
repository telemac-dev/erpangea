from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'user', 'model_name', 'object_id', 'ip_address')
    list_filter = ('action', 'app_label', 'model_name', 'timestamp')
    search_fields = ('object_repr', 'user__email', 'ip_address', 'object_id')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    ordering = ('-timestamp',)

    # Garantia estrita de imutabilidade no Django Admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
