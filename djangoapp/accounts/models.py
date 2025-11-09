from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os


class UserProfile(models.Model):
    """
    Perfil estendido do usuário com informações adicionais
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('supervisor', 'Supervisor'),
        ('user', 'Usuário'),
        ('guest', 'Convidado'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name='Usuário'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        verbose_name='Avatar'
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user',
        verbose_name='Função'
    )
    phone = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name='Telefone'
    )
    department = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Departamento'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Biografia'
    )
    birth_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Data de Nascimento'
    )
    address = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='Endereço'
    )
    city = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Cidade'
    )
    state = models.CharField(
        max_length=2, 
        blank=True,
        verbose_name='Estado'
    )
    zip_code = models.CharField(
        max_length=10, 
        blank=True,
        verbose_name='CEP'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Redimensionar avatar se existir
        if self.avatar:
            img = Image.open(self.avatar.path)
            
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
    
    def get_full_name(self):
        """Retorna o nome completo do usuário"""
        return self.user.get_full_name() or self.user.username
    
    def get_role_display_badge(self):
        """Retorna a classe CSS para o badge da função"""
        role_badges = {
            'admin': 'danger',
            'manager': 'primary',
            'supervisor': 'warning',
            'user': 'success',
            'guest': 'secondary',
        }
        return role_badges.get(self.role, 'secondary')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil quando um usuário é criado"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil quando o usuário é salvo"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class LoginHistory(models.Model):
    """
    Histórico de logins dos usuários
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='login_history',
        verbose_name='Usuário'
    )
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Horário de Login'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    class Meta:
        verbose_name = 'Histórico de Login'
        verbose_name_plural = 'Históricos de Login'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
