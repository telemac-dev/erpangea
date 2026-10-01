import json
from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from django.forms.models import model_to_dict
from .models import AuditLog, AuditActionChoices
from .context import get_current_request, get_client_ip

def record_audit_entry(action, instance=None, app_label=None, model_name=None, object_id=None, object_repr=None, changes=None, user=None):
    request = get_current_request()
    
    ip = get_client_ip(request) if request else None
    ua = request.META.get('HTTP_USER_AGENT', '')[:500] if request else ''
    
    if user is None and request and request.user.is_authenticated:
        user = request.user

    if instance is not None:
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        object_id = str(instance.pk)
        object_repr = str(instance)[:255]

    return AuditLog.objects.create(
        user=user,
        action=action,
        app_label=app_label or 'system',
        model_name=model_name or 'system',
        object_id=object_id or '0',
        object_repr=object_repr or '',
        changes=changes or {},
        ip_address=ip,
        user_agent=ua
    )

# 1. Listeners de Autenticacao
@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    user.reset_failed_logins()
    record_audit_entry(
        action=AuditActionChoices.LOGIN,
        instance=user,
        changes={'info': 'Sessão autenticada com sucesso'},
        user=user
    )

@receiver(user_logged_out)
def handle_user_logged_out(sender, request, user, **kwargs):
    if user:
        record_audit_entry(
            action=AuditActionChoices.LOGOUT,
            instance=user,
            changes={'info': 'Sessão encerrada'},
            user=user
        )

@receiver(user_login_failed)
def handle_user_login_failed(sender, credentials, request, **kwargs):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    email = credentials.get('email') or credentials.get('username')
    user = None
    if email:
        user = User.objects.filter(email=email).first()
        if user:
            user.register_failed_login()

    record_audit_entry(
        action=AuditActionChoices.FAILED_LOGIN,
        app_label='accounts',
        model_name='user',
        object_id=str(user.pk) if user else '0',
        object_repr=email or 'Desconhecido',
        changes={'tentativa_falha': email, 'bloqueado': user.is_locked() if user else False},
        user=user
    )

# 2. Rastreamento Generico de Modelos de Dominio
def register_audit(model):
    """
    Decorator / funcao utilitaria para habilitar auditoria em qualquer modelo Django.
    """
    def _post_save_receiver(sender, instance, created, **kwargs):
        if sender == AuditLog:
            return
        action = AuditActionChoices.CREATE if created else AuditActionChoices.UPDATE
        try:
            changes = json.loads(json.dumps(model_to_dict(instance), default=str))
        except Exception:
            changes = {}
        record_audit_entry(action=action, instance=instance, changes=changes)

    def _post_delete_receiver(sender, instance, **kwargs):
        if sender == AuditLog:
            return
        record_audit_entry(action=AuditActionChoices.DELETE, instance=instance, changes={'status': 'Removido'})

    post_save.connect(_post_save_receiver, sender=model, weak=False, dispatch_uid=f"audit_save_{model._meta.label}")
    post_delete.connect(_post_delete_receiver, sender=model, weak=False, dispatch_uid=f"audit_delete_{model._meta.label}")
    return model
