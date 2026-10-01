import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O endereço de e-mail é obrigatório.'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuário deve possuir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superusuário deve possuir is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class SectorChoices(models.TextChoices):
    ADMINISTRATIVO = 'ADMINISTRATIVO', _('Administrativo')
    COMERCIAL = 'COMERCIAL', _('Comercial')
    TECNICO = 'TECNICO', _('Técnico (Engenharia)')
    FINANCEIRO = 'FINANCEIRO', _('Financeiro')
    TI = 'TI', _('TI / Infraestrutura')

class HierarchyLevel(models.IntegerChoices):
    ASSISTENTE = 1, _('Assistente / Estagiário')
    OPERACIONAL = 2, _('Engenheiro / Analista')
    COORDENACAO = 3, _('Coordenador / Gerente')
    DIRETORIA = 4, _('Diretor / Sócio / RT')

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('endereço de e-mail'), unique=True, max_length=255, db_index=True)
    first_name = models.CharField(_('primeiro nome'), max_length=150, blank=True)
    last_name = models.CharField(_('sobrenome'), max_length=150, blank=True)
    
    is_active = models.BooleanField(_('ativo'), default=True)
    is_staff = models.BooleanField(_('equipe'), default=False)
    date_joined = models.DateTimeField(_('data de cadastro'), default=timezone.now)

    # Seguranca e protecao contra forca bruta
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-date_joined']

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.email

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]

    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def reset_failed_logins(self):
        if self.failed_login_attempts > 0 or self.locked_until:
            self.failed_login_attempts = 0
            self.locked_until = None
            self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def register_failed_login(self, max_attempts=5, lock_duration_minutes=15):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=lock_duration_minutes)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def has_sector_permission(self, sector, min_level=HierarchyLevel.OPERACIONAL):
        """
        Avalia se o usuario possui atribuicao no setor com nivel igual ou superior ao exigido.
        Superusuarios possuem acesso irrestrito.
        """
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return self.sector_assignments.filter(
            sector=sector,
            level__gte=min_level
        ).exists()

    def get_primary_assignment(self):
        """
        Retorna a atribuicao marcada como primaria ou a de maior autoridade hierarquica.
        """
        primary = self.sector_assignments.filter(is_primary=True).first()
        if primary:
            return primary
        return self.sector_assignments.order_by('-level').first()

    def get_highest_level(self):
        assignment = self.sector_assignments.order_by('-level').first()
        return assignment.level if assignment else None

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(_('telefone'), max_length=20, blank=True)
    job_title = models.CharField(_('cargo'), max_length=100, blank=True)
    crea_number = models.CharField(
        _('número CREA/UF'),
        max_length=30,
        blank=True,
        help_text=_('Registro profissional do engenheiro ou técnico no CREA.')
    )
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('perfil de usuário')
        verbose_name_plural = _('perfis de usuários')

    def __str__(self):
        primary = self.user.get_primary_assignment()
        sector_str = f"[{primary.get_sector_display()} - {primary.get_level_display()}]" if primary else "[Sem Setor]"
        return f"Perfil: {self.user.email} {sector_str}"

class UserSectorAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sector_assignments')
    sector = models.CharField(
        _('setor corporativo'),
        max_length=25,
        choices=SectorChoices.choices,
        db_index=True
    )
    level = models.PositiveSmallIntegerField(
        _('nível hierárquico'),
        choices=HierarchyLevel.choices,
        default=HierarchyLevel.OPERACIONAL,
        db_index=True
    )
    is_primary = models.BooleanField(
        _('setor principal'),
        default=False,
        help_text=_('Identifica o setor padrão para relatórios e exibição principal.')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('atribuição de setor e alçada')
        verbose_name_plural = _('atribuições de setores e alçadas')
        unique_together = ('user', 'sector')
        ordering = ['-level', 'sector']

    def save(self, *args, **kwargs):
        # Se for marcado como primario, desmarca os demais setores do usuario
        if self.is_primary:
            UserSectorAssignment.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        primary_badge = " (Principal)" if self.is_primary else ""
        return f"{self.user.email} -> {self.get_sector_display()} [{self.get_level_display()}]{primary_badge}"
