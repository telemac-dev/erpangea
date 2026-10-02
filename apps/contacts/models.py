import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .validators import clean_doc_digits, validate_cpf, validate_cnpj, format_document
from apps.accounts.templatetags.phone_filters import format_phone_br

class ContactTypeChoices(models.TextChoices):
    COMPANY = 'COMPANY', _('Pessoa Jurídica (Empresa)')
    INDIVIDUAL = 'INDIVIDUAL', _('Pessoa Física (Individual)')

class CompanySubtypeChoices(models.TextChoices):
    MATRIZ = 'MATRIZ', _('Matriz / Holding Controladora')
    SPE = 'SPE', _('Sociedade de Propósito Específico (SPE / Empreendimento)')
    FILIAL = 'FILIAL', _('Filial / Unidade Regional')
    CONSORCIO = 'CONSORCIO', _('Consórcio de Empresas')
    OUTRO = 'OUTRO', _('Outro')

class AddressTypeChoices(models.TextChoices):
    CONTACT = 'CONTACT', _('Contato')
    INVOICE = 'INVOICE', _('Endereço de Cobrança')
    DELIVERY = 'DELIVERY', _('Endereço de Entrega / Canteiro')
    OTHER = 'OTHER', _('Outro Endereço')

class DocTypeChoices(models.TextChoices):
    CNPJ = 'CNPJ', _('CNPJ')
    CPF = 'CPF', _('CPF')

class ContactTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Nome do Marcador'), max_length=50, unique=True, db_index=True)
    color = models.CharField(_('Cor Hexadecimal'), max_length=20, default="#2563eb")

    class Meta:
        verbose_name = _('Marcador de Contato')
        verbose_name_plural = _('Marcadores de Contatos')
        ordering = ['name']

    def __str__(self):
        return self.name

class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Classificacao estrutural
    contact_type = models.CharField(
        _('Tipo de Contato'),
        max_length=15,
        choices=ContactTypeChoices.choices,
        default=ContactTypeChoices.COMPANY,
        db_index=True
    )
    company_subtype = models.CharField(
        _('Subtipo Empresarial'),
        max_length=20,
        choices=CompanySubtypeChoices.choices,
        default=CompanySubtypeChoices.MATRIZ,
        blank=True,
        db_index=True,
        help_text=_('Classificação jurídica: Matriz, SPE, Filial ou Consórcio.')
    )
    address_type = models.CharField(
        _('Tipo de Endereço / Vínculo'),
        max_length=15,
        choices=AddressTypeChoices.choices,
        default=AddressTypeChoices.CONTACT,
        db_index=True
    )

    # Identificacao basica
    name = models.CharField(_('Nome / Razão Social'), max_length=255, db_index=True)
    trade_name = models.CharField(_('Nome Fantasia'), max_length=255, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_('Empresa Vinculada (Holding / Controladora)')
    )

    # Identificacao fiscal brasileira
    doc_type = models.CharField(
        _('Tipo de Documento'),
        max_length=10,
        choices=DocTypeChoices.choices,
        default=DocTypeChoices.CNPJ
    )
    doc_number = models.CharField(_('Número do Documento'), max_length=25, blank=True, db_index=True)
    state_registration = models.CharField(_('Inscrição Estadual (IE)'), max_length=30, blank=True)
    municipal_registration = models.CharField(_('Inscrição Municipal (IM)'), max_length=30, blank=True)
    suframa_code = models.CharField(_('Código SUFRAMA'), max_length=30, blank=True)

    # Endereco estruturado
    street = models.CharField(_('Logradouro'), max_length=200, blank=True)
    number = models.CharField(_('Número'), max_length=20, blank=True)
    complement = models.CharField(_('Complemento'), max_length=100, blank=True)
    neighborhood = models.CharField(_('Bairro'), max_length=100, blank=True)
    city = models.CharField(_('Cidade'), max_length=100, blank=True, db_index=True)
    state = models.CharField(_('Estado / UF'), max_length=2, blank=True, db_index=True)
    postal_code = models.CharField(_('CEP'), max_length=10, blank=True)
    country = models.CharField(_('País'), max_length=50, default='Brasil', blank=True)

    # Comunicacao e canais
    phone = models.CharField(_('Telefone'), max_length=25, blank=True)
    mobile = models.CharField(_('Celular'), max_length=25, blank=True)
    email = models.EmailField(_('E-mail'), blank=True, db_index=True)
    website = models.URLField(_('Site Oficial'), blank=True)
    job_title = models.CharField(_('Cargo / Função'), max_length=100, blank=True)

    # Comercial e relacionamento
    salesperson = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_contacts',
        verbose_name=_('Vendedor / Responsável')
    )
    payment_terms = models.CharField(_('Condições de Pagamento'), max_length=50, blank=True)
    tags = models.ManyToManyField(ContactTag, blank=True, related_name='contacts', verbose_name=_('Marcadores'))

    # Midia e governanca
    avatar = models.ImageField(_('Foto / Logotipo'), upload_to='contacts/avatars/', null=True, blank=True)
    internal_notes = models.TextField(_('Anotações Internas'), blank=True)
    is_active = models.BooleanField(_('Ativo'), default=True, db_index=True)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Contato')
        verbose_name_plural = _('Contatos')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['doc_number', 'is_active']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['contact_type', 'company_subtype']),
        ]

    @property
    def is_company(self):
        return self.contact_type == ContactTypeChoices.COMPANY

    @property
    def is_individual(self):
        return self.contact_type == ContactTypeChoices.INDIVIDUAL

    @property
    def complete_name(self):
        try:
            if self.parent_id and self.parent:
                if self.is_company:
                    return f"{self.parent.name} / {self.name}"
                return f"{self.parent.name}, {self.name}"
        except Exception:
            pass
        return self.name

    @property
    def formatted_doc_number(self):
        if not self.doc_number:
            return ""
        return format_document(self.doc_number, self.doc_type)

    @property
    def display_address(self):
        parts = []
        if self.street:
            addr = self.street
            if self.number:
                addr += f", {self.number}"
            if self.complement:
                addr += f" ({self.complement})"
            parts.append(addr)
        if self.neighborhood:
            parts.append(self.neighborhood)
        if self.city or self.state:
            loc = f"{self.city}/{self.state}" if self.city and self.state else (self.city or self.state)
            parts.append(loc)
        if self.postal_code:
            parts.append(f"CEP: {self.postal_code}")
        return " - ".join(parts) if parts else self.country

    def clean(self):
        super().clean()
        
        # 1. Impede auto-referência e ciclos na empresa mãe
        if self.parent_id:
            if self.pk and self.parent_id == self.pk:
                raise ValidationError({'parent': _("Um contato não pode ser sua própria empresa vinculada.")})
            
            if self.pk:
                current_parent = self.parent
                visited = {self.pk}
                while current_parent:
                    if current_parent.pk in visited:
                        raise ValidationError({'parent': _("Ciclo hierárquico detectado: a empresa vinculada já descende deste contato.")})
                    visited.add(current_parent.pk)
                    current_parent = current_parent.parent

        # 2. Validação e normalização de CNPJ / CPF
        if self.doc_number:
            raw_digits = clean_doc_digits(self.doc_number)
            
            if self.doc_type == DocTypeChoices.CPF:
                validate_cpf(raw_digits)
            elif self.doc_type == DocTypeChoices.CNPJ:
                validate_cnpj(raw_digits)

            # Verificação de duplicidade entre contatos ativos
            qs = Contact.objects.filter(doc_number=raw_digits, is_active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                existing = qs.first()
                raise ValidationError({
                    'doc_number': _(f"Este número de documento já está cadastrado para o contato ativo '{existing.name}'.")
                })
            
            self.doc_number = raw_digits

    def save(self, *args, **kwargs):
        if self.doc_number:
            self.doc_number = clean_doc_digits(self.doc_number)
        if self.phone:
            self.phone = format_phone_br(self.phone)
        if self.mobile:
            self.mobile = format_phone_br(self.mobile)
        super().save(*args, **kwargs)

    def archive(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def unarchive(self):
        self.is_active = True
        self.save(update_fields=['is_active'])

    def __str__(self):
        return self.complete_name
