from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.accounts.models import SectorChoices

User = get_user_model()

class Command(BaseCommand):
    help = "Cria um novo colaborador no ERPangea com setor e credenciais predefinidas"

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help="E-mail corporativo do colaborador")
        parser.add_argument('--password', required=True, help="Senha inicial de acesso")
        parser.add_argument('--first-name', default='', help="Primeiro nome")
        parser.add_argument('--last-name', default='', help="Sobrenome")
        parser.add_argument(
            '--sector',
            default=SectorChoices.TECNICO.value,
            choices=[s.value for s in SectorChoices],
            help="Setor corporativo (ADMINISTRATIVO, COMERCIAL, TECNICO, FINANCEIRO, TI)"
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

        # O perfil e criado automaticamente pelo post_save signal
        profile = user.profile
        profile.sector = options['sector']
        profile.job_title = options['job_title']
        profile.crea_number = options['crea']
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f"Colaborador criado com sucesso!\n"
            f" -> ID: {user.pk}\n"
            f" -> E-mail: {user.email}\n"
            f" -> Setor: {profile.get_sector_display()}\n"
            f" -> CREA: {profile.crea_number or 'Não informado'}"
        ))
