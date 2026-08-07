from django.db import models
from django.contrib.auth.models import AbstractUser

class UserRoleChoices(models.TextChoices):
    ADMINISTRATOR = 'ADMINISTRATOR', 'Administrador'
    MANAGER = 'MANAGER', 'Gerente'
    COLLABORATOR = 'COLLABORATOR', 'Colaborador'

class CustomUser(AbstractUser):
    role = models.CharField(
        'Nível de Acesso / Perfil',
        max_length=20,
        choices=UserRoleChoices.choices,
        default=UserRoleChoices.COLLABORATOR
    )

    @property
    def is_admin(self):
        return self.role == UserRoleChoices.ADMINISTRATOR or self.is_superuser

    @property
    def is_manager(self):
        return self.role in [UserRoleChoices.ADMINISTRATOR, UserRoleChoices.MANAGER] or self.is_superuser

    @property
    def can_access_financials(self):
        return self.role in [UserRoleChoices.ADMINISTRATOR, UserRoleChoices.MANAGER] or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
