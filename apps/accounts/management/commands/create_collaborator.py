from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.accounts.models import SectorChoices, HierarchyLevel, UserSectorAssignment

User = get_user_model()

class Command(BaseCommand):
    help = "Cria um novo colaborador com setor primario, nivel hierarquico e setores adicionais"

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help="E-mail corporativo do colaborador")
        parser.add_argument('--password', required=True, help="Senha inicial de acesso")
        parser.add_argument('--first-name', default='', help="Primeiro nome")
        parser.add_argument('--last-name', default='', help="Sobrenome")
        parser.add_argument(
            '--sector',
            default=SectorChoices.TECNICO.value,
            choices=[s.value for s in SectorChoices],
            help="Setor primário (ADMINISTRATIVO, COMERCIAL, TECNICO, FINANCEIRO, TI)"
        )
        parser.add_argument(
            '--level',
            type=int,
            default=HierarchyLevel.OPERACIONAL.value,
            choices=[1, 2, 3, 4],
            help="Nível hierárquico no setor primário (1=Assistente, 2=Operacional, 3=Coordenação, 4=Diretoria)"
        )
        parser.add_argument(
            '--extra-sectors',
            default='',
            help="Setores adicionais no formato 'SETOR:NIVEL,SETOR:NIVEL' (ex: 'COMERCIAL:3,FINANCEIRO:4')"
        )
        parser.add_argument('--job-title', default='', help="Cargo ou especialidade técnica")
        parser.add_argument('--crea', default='', help="Número de registro no CREA e UF")
        parser.add_argument('--is-staff', action='store_true', help="Concede acesso ao Django Admin")

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        if User.objects.filter(email=email).exists():
            raise CommandError(f"Usuário com e-mail '{email}' já existe no sistema.")

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=options['first_name'],
            last_name=options['last_name'],
            is_staff=options['is_staff']
        )

        # Atualiza perfil
        profile = user.profile
        profile.job_title = options['job_title']
        profile.crea_number = options['crea']
        profile.save()

        # Configura setor primario
        primary_sector = options['sector']
        primary_level = options['level']
        
        # O signal pode ter criado uma atribuicao padrao, atualizamos ou criamos
        assignment, created = UserSectorAssignment.objects.get_or_create(
            user=user,
            sector=primary_sector,
            defaults={'level': primary_level, 'is_primary': True}
        )
        if not created:
            assignment.level = primary_level
            assignment.is_primary = True
            assignment.save()

        # Processa setores adicionais (Multi-Setor)
        extra_str = options['extra_sectors'].strip()
        if extra_str:
            for item in extra_str.split(','):
                item = item.strip()
                if not item:
                    continue
                parts = item.split(':')
                sec_name = parts[0].strip().upper()
                sec_lvl = int(parts[1].strip()) if len(parts) > 1 else HierarchyLevel.OPERACIONAL.value
                
                if sec_name in [s.value for s in SectorChoices]:
                    UserSectorAssignment.objects.update_or_create(
                        user=user,
                        sector=sec_name,
                        defaults={'level': sec_lvl, 'is_primary': False}
                    )

        assignments_desc = ", ".join(
            f"{a.get_sector_display()} ({a.get_level_display()})" for a in user.sector_assignments.all()
        )

        self.stdout.write(self.style.SUCCESS(
            f"Colaborador criado com sucesso!\n"
            f" -> ID: {user.pk}\n"
            f" -> E-mail: {user.email}\n"
            f" -> Atribuições: {assignments_desc}\n"
            f" -> CREA: {profile.crea_number or 'Não informado'}"
        ))
