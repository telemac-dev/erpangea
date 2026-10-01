import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

class AuditActionChoices(models.TextChoices):
    CREATE = 'CREATE', _('Criação')
    UPDATE = 'UPDATE', _('Atualização')
    DELETE = 'DELETE', _('Exclusão')
    LOGIN = 'LOGIN', _('Autenticação com Sucesso')
    LOGOUT = 'LOGOUT', _('Encerramento de Sessão')
    FAILED_LOGIN = 'FAILED_LOGIN', _('Tentativa Falha de Login')
    EXPORT = 'EXPORT', _('Exportação de Dados')

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        db_index=True
    )
    action = models.CharField(
        max_length=20,
        choices=AuditActionChoices.choices,
        db_index=True
    )
    app_label = models.CharField(max_length=50, db_index=True)
    model_name = models.CharField(max_length=50, db_index=True)
    object_id = models.CharField(max_length=255, db_index=True)
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(default=dict, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('registro de auditoria')
        verbose_name_plural = _('trilha de auditoria')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['app_label', 'model_name', 'object_id']),
            models.Index(fields=['timestamp', 'action']),
        ]

    def save(self, *args, **kwargs):
        # Bloqueia alteracao de registros pre-existentes (Imutabilidade estrita)
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise PermissionDenied("Registros da trilha de auditoria são imutáveis e não podem ser alterados.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Bloqueia exclusao de registros (Imutabilidade estrita)
        raise PermissionDenied("Registros da trilha de auditoria são imutáveis e não podem ser excluídos.")

    def __str__(self):
        return f"[{self.timestamp:%d/%m/%Y %H:%M:%S}] {self.action} - {self.model_name}:{self.object_id} por {self.user or 'Sistema'}"
