from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import SectorChoices

class Command(BaseCommand):
    help = "Inicializa grupos corporativos (RBAC) e politicas de permissao para a Pangea Engenharia"

    def handle(self, *args, **options):
        self.stdout.write("==> Provisionando Grupos Corporativos (RBAC)...")
        
        roles = {
            SectorChoices.ADMINISTRATIVO.value: "Setor Administrativo - Cadastros gerais e lancamentos operacionais",
            SectorChoices.COMERCIAL.value: "Setor Comercial - Oportunidades, propostas e formalizacao",
            SectorChoices.TECNICO.value: "Setor Tecnico / Engenharia - Projetos, EDMS, medioes e vistorias",
            SectorChoices.FINANCEIRO.value: "Setor Financeiro - Aprovacao de gastos, notas fiscais e tesouraria",
            SectorChoices.TI.value: "Setor de TI & Infraestrutura - Acesso total e configuracoes",
        }

        for role_name in roles.keys():
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f" [OK] Grupo criado: {role_name}"))
            else:
                self.stdout.write(f" [INFO] Grupo ja existente: {role_name}")

        self.stdout.write(self.style.SUCCESS("==> Estrutura RBAC provisionada com sucesso."))
