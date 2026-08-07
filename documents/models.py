from django.db import models
from django.conf import settings
from projects.models import Project

class DocumentCategoryChoices(models.TextChoices):
    DESENHO_CAD = 'DESENHO_CAD', 'Desenho / Prancha CAD'
    MODELO_BIM = 'MODELO_BIM', 'Modelo 3D / BIM'
    MEMORIAL_CALCULO = 'MEMORIAL_CALCULO', 'Memorial de Cálculo'
    LAUDO_GEOTECNICO = 'LAUDO_GEOTECNICO', 'Laudo Geotécnico / Vistoria'
    SONDAGEM_SPT = 'SONDAGEM_SPT', 'Ensaio de Sondagem SPT'
    ART_CREA = 'ART_CREA', 'ART / Anotação de Resp. Técnica'
    CONTRATO_ADM = 'CONTRATO_ADM', 'Contrato / Documento Administrativo'
    OUTRO = 'OUTRO', 'Outro Documento'

class DocumentStatusChoices(models.TextChoices):
    EM_ELABORACAO = 'EM_ELABORACAO', 'Em Elaboração'
    EM_REVISAO = 'EM_REVISAO', 'Em Revisão'
    AGUARDANDO_APROVACAO = 'AGUARDANDO_APROVACAO', 'Aguardando Aprovação'
    APROVADO = 'APROVADO', 'Aprovado'
    REJEITADO = 'REJEITADO', 'Rejeitado'
    OBSOLETO = 'OBSOLETO', 'Obsoleto'


class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='documents', verbose_name='Projeto Associado')
    title = models.CharField('Título do Documento', max_length=255)
    category = models.CharField('Categoria Técnica', max_length=50, choices=DocumentCategoryChoices.choices, default=DocumentCategoryChoices.DESENHO_CAD)
    file = models.FileField('Arquivo', upload_to='documents/%Y/%m/')
    
    revision = models.CharField('Código da Revisão', max_length=10, default='R00')
    status = models.CharField('Status de Aprovação', max_length=50, choices=DocumentStatusChoices.choices, default=DocumentStatusChoices.EM_ELABORACAO)
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents', verbose_name='Enviado por')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_documents', verbose_name='Aprovado por')
    
    notes = models.TextField('Observações / Histórico', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Documento Técnico'
        verbose_name_plural = 'Documentos Técnicos'

    def __str__(self):
        return f"{self.title} ({self.revision}) - {self.get_category_display()}"


class DocumentRevision(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='revisions', verbose_name='Documento Principal')
    revision_number = models.CharField('Revisão', max_length=10)
    file = models.FileField('Arquivo da Revisão', upload_to='documents/revisions/%Y/%m/')
    changes_summary = models.TextField('Descrição das Alterações')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Enviado por')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Revisão Documental'
        verbose_name_plural = 'Revisões Documentais'

    def __str__(self):
        return f"{self.document.title} - {self.revision_number}"
