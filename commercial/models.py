from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from contacts.models import Contact
from datetime import date
import datetime

class DisciplineEnum(models.TextChoices):
    FUNDACOES = 'FUNDACOES', 'Fundações'
    CONTENCOES = 'CONTENCOES', 'Contenções'
    OBRAS_TERRA = 'OBRAS_TERRA', 'Obras de Terra'
    ESTRUTURAS = 'ESTRUTURAS', 'Estruturas'
    PAVIMENTACAO = 'PAVIMENTACAO', 'Pavimentação'
    CONSULTORIA = 'CONSULTORIA', 'Consultoria'

class ProposalStatusEnum(models.TextChoices):
    RASCUNHO = 'RASCUNHO', 'Rascunho'
    ENVIADA = 'ENVIADA', 'Enviada'
    EM_NEGOCIACAO = 'EM_NEGOCIACAO', 'Em Negociação'
    APROVADA = 'APROVADA', 'Aprovada'
    DECLINADA = 'DECLINADA', 'Declinada'

class Proposal(models.Model):
    codigo_proposta = models.CharField(max_length=50, unique=True, blank=True)
    cliente = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name='proposals')
    disciplina_principal = models.CharField(max_length=20, choices=DisciplineEnum.choices)
    valor_global = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=ProposalStatusEnum.choices, default=ProposalStatusEnum.RASCUNHO)
    validade = models.DateField()

    def save(self, *args, **kwargs):
        if not self.codigo_proposta:
            year = date.today().year
            # Gera um código simples sequencial (Em produção precisaria tratar concorrência)
            count = Proposal.objects.filter(codigo_proposta__startswith=f"PROP-{year}").count() + 1
            self.codigo_proposta = f"PROP-{year}-{count:04d}"
            
        if self.pk:
            old_instance = Proposal.objects.get(pk=self.pk)
            # Regra: Proposta aprovada trava a edição de valores
            if old_instance.status == ProposalStatusEnum.APROVADA and self.status == ProposalStatusEnum.APROVADA:
                if old_instance.valor_global != self.valor_global or old_instance.disciplina_principal != self.disciplina_principal:
                    raise ValidationError("Não é possível alterar valores ou escopo de uma proposta já aprovada.")
                    
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_proposta} - {self.cliente}"

class BillingModeEnum(models.TextChoices):
    MEDICAO_MENSAL = 'MEDICAO_MENSAL', 'Medição Mensal'
    PRECO_GLOBAL_MARCOS = 'PRECO_GLOBAL_MARCOS', 'Preço Global por Marcos'
    HORAS_TECNICAS = 'HORAS_TECNICAS', 'Horas Técnicas'

class Contract(models.Model):
    proposta = models.OneToOneField(Proposal, on_delete=models.PROTECT, related_name='contract')
    numero_contrato = models.CharField(max_length=50, unique=True, blank=True)
    data_assinatura = models.DateField(null=True, blank=True)
    data_vigencia_inicio = models.DateField()
    data_vigencia_fim = models.DateField()
    valor_total_contratado = models.DecimalField(max_digits=12, decimal_places=2)
    modalidade_cobranca = models.CharField(max_length=25, choices=BillingModeEnum.choices)
    documento_assinado = models.FileField(upload_to='contracts/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.numero_contrato:
            year = date.today().year
            count = Contract.objects.filter(numero_contrato__startswith=f"CTR-{year}").count() + 1
            self.numero_contrato = f"CTR-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.numero_contrato

class OSStatusEnum(models.TextChoices):
    PLANEJAMENTO = 'PLANEJAMENTO', 'Planejamento'
    ATIVA = 'ATIVA', 'Ativa'
    SUSPENSA = 'SUSPENSA', 'Suspensa'
    CONCLUIDA = 'CONCLUIDA', 'Concluída'

class WorkOrder(models.Model):
    contrato = models.ForeignKey(Contract, on_delete=models.PROTECT, related_name='work_orders')
    numero_os = models.CharField(max_length=50, unique=True, blank=True)
    coordenador_tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, limit_choices_to={'profile__setor': 'TECNICO'})
    status = models.CharField(max_length=20, choices=OSStatusEnum.choices, default=OSStatusEnum.PLANEJAMENTO)

    def clean(self):
        # Regra de Negócio: OS só pode ser ativada caso o Contrato tenha documento assinado anexado
        if self.status == OSStatusEnum.ATIVA and not self.contrato.documento_assinado:
            raise ValidationError("Uma Ordem de Serviço não pode ser ATIVA sem que o contrato possua o PDF assinado.")

    def save(self, *args, **kwargs):
        self.clean()
        if not self.numero_os:
            year = date.today().year
            count = WorkOrder.objects.filter(numero_os__startswith=f"OS-{year}").count() + 1
            self.numero_os = f"OS-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_os} ({self.status})"
