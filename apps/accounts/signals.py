from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile, UserSectorAssignment, SectorChoices, HierarchyLevel

@receiver(post_save, sender=User)
def create_user_profile_and_default_sector(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)
        
        # Garante atribuicao inicial padrao caso nenhuma tenha sido criada previamente
        if not instance.sector_assignments.exists():
            default_sector = SectorChoices.TI if instance.is_superuser else SectorChoices.TECNICO
            default_level = HierarchyLevel.DIRETORIA if instance.is_superuser else HierarchyLevel.OPERACIONAL
            UserSectorAssignment.objects.create(
                user=instance,
                sector=default_sector,
                level=default_level,
                is_primary=True
            )
