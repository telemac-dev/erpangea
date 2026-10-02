from apps.audit_log.signals import register_audit
from .models import Contact, ContactTag

# Conecta auditoria automatica para os modelos de contatos
register_audit(Contact)
register_audit(ContactTag)
