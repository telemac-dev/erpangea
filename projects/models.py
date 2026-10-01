from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from commercial.models import WorkOrder

class ProjectStatusEnum(models.TextChoices):
    BRIEFING = 'BRIEFING', 'Briefing'
    ESTUDOS_PRELIMINARES = 'ESTUDOS_PRELIMINARES', 'Estudos Preliminares'
    CALCULO_DIMENSIONAMENTO = 'CALCULO_DIMENSIONAMENTO', 'Cálculo e Dimensionamento'
    DESENHO_DETALHAMENTO = 'DESENHO_DETALHAMENTO', 'Desenho e Detalhamento'
    REVISAO_INTERNA = 'REVISAO_INTERNA', 'Revisão Interna'
    ENTREGUE = 'ENTREGUE', 'Entregue'

class Project(models.Model):
    ordem_servico = models.OneToOneField(WorkOrder, on_delete=models.PROTECT, related_name='project')
    nome_projeto = models.CharField(max_length=255)
    localizacao = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=30, choices=ProjectStatusEnum.choices, default=ProjectStatusEnum.BRIEFING)
    percentual_avanco = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def clean(self):
        # Regra: Fechamento (Entregue) exige ART homologada no EDMS.
        if self.status == ProjectStatusEnum.ENTREGUE:
            # Precisa checar dinamicamente para evitar import circular com edms_docs
            from edms_docs.models import ProjectDocument, DocumentTypeEnum, RevisionStatusEnum
            
            tem_art_aprovada = ProjectDocument.objects.filter(
                projeto=self,
                tipo=DocumentTypeEnum.ART_CREA,
                revisions__status__in=[RevisionStatusEnum.APROVADO_CLIENTE, RevisionStatusEnum.APROVADO_INTERNO] # Assumindo aprovação final
            ).exists()
            
            if not tem_art_aprovada:
                raise ValidationError("O projeto não pode ser Entregue sem pelo menos uma ART aprovada anexada.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome_projeto} ({self.ordem_servico.numero_os})"

class ProjectPhase(models.Model):
    projeto = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='phases')
    nome_etapa = models.CharField(max_length=150)
    concluida = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nome_etapa} - {self.projeto.nome_projeto}"

class TaskStatusEnum(models.TextChoices):
    A_FAZER = 'A_FAZER', 'A Fazer'
    EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
    IMPEDIMENTO = 'IMPEDIMENTO', 'Com Impedimento'
    CONCLUIDA = 'CONCLUIDA', 'Concluída'

class TaskPriorityEnum(models.TextChoices):
    BAIXA = 'BAIXA', 'Baixa'
    NORMAL = 'NORMAL', 'Normal'
    ALTA = 'ALTA', 'Alta'
    URGENTE = 'URGENTE', 'Urgente'

class Task(models.Model):
    fase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, related_name='tasks')
    titulo = models.CharField(max_length=200)
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    prioridade = models.CharField(max_length=20, choices=TaskPriorityEnum.choices, default=TaskPriorityEnum.NORMAL)
    status = models.CharField(max_length=20, choices=TaskStatusEnum.choices, default=TaskStatusEnum.A_FAZER)
    horas_previstas = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    horas_gastas = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Aqui no futuro podemos disparar um Signal notificando o Coordenador Técnico (WorkOrder.coordenador_tecnico) se status == IMPEDIMENTO
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
