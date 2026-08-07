from django.db import models
from django.conf import settings
from django.utils import timezone

class ContactRoleChoices(models.TextChoices):
    CLIENT = 'CLIENT', 'Cliente'
    SUPPLIER = 'SUPPLIER', 'Fornecedor'
    PARTNER = 'PARTNER', 'Parceiro'
    PUBLIC_BODY = 'PUBLIC_BODY', 'Órgão Público'
    PROFESSIONAL = 'PROFESSIONAL', 'Profissional'
    SUBCONTRACTOR = 'SUBCONTRACTOR', 'Subcontratado'

class PersonTypeChoices(models.TextChoices):
    PF = 'PF', 'Pessoa Física'
    PJ = 'PJ', 'Pessoa Jurídica'

class InteractionTypeChoices(models.TextChoices):
    REUNIAO = 'REUNIAO', 'Reunião'
    LIGACAO = 'LIGACAO', 'Ligação'
    EMAIL = 'EMAIL', 'E-mail'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
    VISITA = 'VISITA', 'Visita Técnica'
    OUTRO = 'OUTRO', 'Outro'

class ContactRole(models.Model):
    name = models.CharField(max_length=50, choices=ContactRoleChoices.choices, unique=True)

    def __str__(self):
        return self.get_name_display()

class Contact(models.Model):
    name = models.CharField('Nome ou Razão Social', max_length=255)
    trade_name = models.CharField('Nome Fantasia', max_length=255, blank=True)
    person_type = models.CharField('Tipo de Pessoa', max_length=2, choices=PersonTypeChoices.choices, default=PersonTypeChoices.PJ)
    document = models.CharField('CPF / CNPJ', max_length=20, blank=True)
    
    email = models.EmailField('E-mail', blank=True)
    phone = models.CharField('Telefone', max_length=30, blank=True)
    zip_code = models.CharField('CEP', max_length=10, blank=True)
    address = models.CharField('Endereço', max_length=255, blank=True)
    city = models.CharField('Cidade', max_length=100, blank=True)
    state = models.CharField('UF', max_length=2, blank=True)
    website = models.URLField('Website', blank=True)
    
    notes = models.TextField('Observações', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    roles = models.ManyToManyField(ContactRole, related_name='contacts', verbose_name='Funções')
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'

    @property
    def formatted_document(self):
        from .utils import format_cpf, format_cnpj
        if not self.document:
            return ""
        if self.person_type == PersonTypeChoices.PF:
            return format_cpf(self.document)
        return format_cnpj(self.document)

    def __str__(self):
        return self.name
class Interaction(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='interactions', verbose_name='Contato')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='interactions', verbose_name='Usuário Responsável')
    date = models.DateTimeField('Data e Hora', default=timezone.now)
    interaction_type = models.CharField('Tipo', max_length=50, choices=InteractionTypeChoices.choices, default=InteractionTypeChoices.REUNIAO)
    subject = models.CharField('Assunto', max_length=255)
    description = models.TextField('Descrição')
    
    next_action = models.CharField('Próxima Ação', max_length=255, blank=True)
    next_action_deadline = models.DateField('Prazo da Próxima Ação', null=True, blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Interação'
        verbose_name_plural = 'Interações'

    def __str__(self):
        return f"{self.get_interaction_type_display()} - {self.subject} ({self.contact.name})"
