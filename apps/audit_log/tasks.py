from celery import shared_task
from .models import AuditLog

@shared_task(name='audit_log.record_async', bind=True, max_retries=3)
def record_audit_log_async(self, action, app_label, model_name, object_id, object_repr, changes, user_id=None, ip_address=None, user_agent=''):
    try:
        AuditLog.objects.create(
            user_id=user_id,
            action=action,
            app_label=app_label,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception as exc:
        self.retry(exc=exc, countdown=5)
