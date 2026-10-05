from apps.audit_log.signals import register_audit
from .models import (
    CommercialProposal,
    ProposalScopeItem,
    ProposalInputRequirement,
    LegalContract
)

# Conecta auditoria automatica para todas as entidades comerciais e contratuais
register_audit(CommercialProposal)
register_audit(ProposalScopeItem)
register_audit(ProposalInputRequirement)
register_audit(LegalContract)
