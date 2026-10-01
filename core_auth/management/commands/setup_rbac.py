from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core_auth.models import SectorEnum

class Command(BaseCommand):
    help = 'Cria os grupos de permissões baseados nos setores'

    def handle(self, *args, **options):
        setores = [
            SectorEnum.ADMINISTRATIVO.label,
            SectorEnum.COMERCIAL.label,
            SectorEnum.TECNICO.label,
            SectorEnum.FINANCEIRO.label,
            SectorEnum.TI.label,
        ]

        for setor in setores:
            group, created = Group.objects.get_or_create(name=setor)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{setor}" criado com sucesso.'))
            else:
                self.stdout.write(f'Grupo "{setor}" já existe.')
                
        self.stdout.write(self.style.SUCCESS('RBAC inicializado.'))
