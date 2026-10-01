from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Proposal, Contract, ProposalStatusEnum, BillingModeEnum
from datetime import date, timedelta

@receiver(post_save, sender=Proposal)
def generate_contract_on_approval(sender, instance, **kwargs):
    # Regra de Negócio: Aprovação da Proposta gera minuta de contrato
    if instance.status == ProposalStatusEnum.APROVADA:
        if not hasattr(instance, 'contract'):
            Contract.objects.create(
                proposta=instance,
                data_vigencia_inicio=date.today(),
                data_vigencia_fim=date.today() + timedelta(days=365), # default 1 ano
                valor_total_contratado=instance.valor_global,
                modalidade_cobranca=BillingModeEnum.PRECO_GLOBAL_MARCOS # default a definir depois
            )
