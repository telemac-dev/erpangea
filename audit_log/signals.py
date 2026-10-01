from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import ActivityLog, ActionEnum
from .middleware import get_current_request
from core_auth.models import User, UserProfile
from contacts.models import Contact, Address, ContactPerson
from commercial.models import Proposal, Contract, WorkOrder
from projects.models import Project, ProjectPhase, Task
from edms_docs.models import ProjectDocument, DocumentRevision
from measurements.models import MeasurementSheet, MeasurementItem
from invoices.models import ServiceInvoice, AccountReceivable
from financial.models import AccountPayable
import json

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def record_activity(sender, instance, created=False, deleted=False, **kwargs):
    if sender == ActivityLog:
        return # Evita loop infinito

    request = get_current_request()
    user = None
    ip = None
    ua = None
    
    if request:
        user = request.user if request.user.is_authenticated else None
        ip = get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')[:255]

    acao = ActionEnum.CREATE if created else (ActionEnum.DELETE if deleted else ActionEnum.UPDATE)
    
    # Prepara changes
    changes = None
    if not deleted:
        try:
            # Serializa para JSON de forma simples, no mundo real compararia com o estado anterior (pre_save)
            changes = json.dumps(model_to_dict(instance), default=str)
        except Exception:
            pass
            
    ActivityLog.objects.create(
        usuario=user,
        ip_address=ip,
        user_agent=ua,
        acao=acao,
        app_label=sender._meta.app_label,
        model_name=sender._meta.model_name,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        changes=changes
    )

# Modelos operacionais a serem auditados na Fase 1
AUDIT_MODELS = [Contact, Address, ContactPerson, User, UserProfile, Proposal, Contract, WorkOrder, Project, ProjectPhase, Task, ProjectDocument, DocumentRevision, MeasurementSheet, MeasurementItem, ServiceInvoice, AccountReceivable, AccountPayable]

for model in AUDIT_MODELS:
    post_save.connect(record_activity, sender=model)
    post_delete.connect(lambda sender, instance, **kwargs: record_activity(sender, instance, deleted=True, **kwargs), sender=model)
