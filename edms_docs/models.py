from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from projects.models import Project

class DocumentTypeEnum(models.TextChoices):
    SONDAGEM_SPT_CPTU = 'SONDAGEM_SPT_CPTU', 'Sondagem SPT/CPTU'
    MEMORIA_CALCULO = 'MEMORIA_CALCULO', 'Memória de Cálculo'
    PRANCHA_CAD_BIM = 'PRANCHA_CAD_BIM', 'Prancha CAD/BIM'
    RELATORIO_TECNICO = 'RELATORIO_TECNICO', 'Relatório Técnico'
    ART_CREA = 'ART_CREA', 'ART CREA'
    OUTRO = 'OUTRO', 'Outro'

class RevisionStatusEnum(models.TextChoices):
    EM_ELABORACAO = 'EM_ELABORACAO', 'Em Elaboração'
    APROVADO_INTERNO = 'APROVADO_INTERNO', 'Aprovado Internamente'
    EMITIDO_CLIENTE = 'EMITIDO_CLIENTE', 'Emitido para o Cliente'
    APROVADO_CLIENTE = 'APROVADO_CLIENTE', 'Aprovado pelo Cliente'

class ProjectDocument(models.Model):
    projeto = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    tipo = models.CharField(max_length=30, choices=DocumentTypeEnum.choices)
    codigo_identificador = models.CharField(max_length=100, unique=True, help_text="Ex: PG-PROJ-01-EST-001")
    titulo = models.CharField(max_length=255)

    def __str__(self):
        return f"[{self.codigo_identificador}] {self.titulo}"

class DocumentRevision(models.Model):
    documento = models.ForeignKey(ProjectDocument, on_delete=models.CASCADE, related_name='revisions')
    revisao = models.CharField(max_length=10, blank=True)
    arquivo = models.FileField(upload_to='edms_vault/')
    data_upload = models.DateTimeField(auto_now_add=True)
    enviado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=30, choices=RevisionStatusEnum.choices, default=RevisionStatusEnum.EM_ELABORACAO)
    notas_alteracao = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.revisao:
            # Auto-incrementa a revisão: R00, R01, R02...
            count = DocumentRevision.objects.filter(documento=self.documento).count()
            self.revisao = f"R{count:02d}"
            
        # Regras de extensão (validação simplificada, ideal em form ou validator)
        if self.arquivo:
            name = self.arquivo.name.lower()
            allowed = ['.dwg', '.dxf', '.pdf', '.xlsx', '.cype', '.gsz', '.plx']
            if not any(name.endswith(ext) for ext in allowed):
                raise ValidationError("Extensão de arquivo não permitida para o repositório técnico.")
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.documento.codigo_identificador} - Rev {self.revisao}"
