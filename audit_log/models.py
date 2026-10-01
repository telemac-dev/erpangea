from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

class ActionEnum(models.TextChoices):
    CREATE = 'CREATE', 'Criar'
    UPDATE = 'UPDATE', 'Atualizar'
    DELETE = 'DELETE', 'Deletar'
    LOGIN = 'LOGIN', 'Login'
    LOGOUT = 'LOGOUT', 'Logout'
    EXPORT = 'EXPORT', 'Exportar'

class ActivityLog(models.fields.related.ForeignKey):
    pass # corrigindo abaixo

class ActivityLog(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    acao = models.CharField(max_length=20, choices=ActionEnum.choices)
    app_label = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.acao} - {self.model_name} por {self.usuario} em {self.timestamp}"
