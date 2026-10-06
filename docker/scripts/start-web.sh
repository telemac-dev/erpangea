#!/bin/bash
set -e

echo "==> [ERPangea] Executando migrações do banco de dados..."
python manage.py migrate --noinput

echo "==> [ERPangea] Provisionando grupos de permissão RBAC..."
python manage.py setup_rbac || true

echo "==> [ERPangea] Garantindo usuário administrador padrão..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.getenv('ADMIN_EMAIL', 'admin@pangea.eng.br')
password = os.getenv('ADMIN_PASSWORD', 'Pangea#2026')
admin, _ = User.objects.get_or_create(
    email=email,
    defaults={'first_name': 'Administrador', 'last_name': 'Pangea', 'is_staff': True, 'is_superuser': True}
)
admin.set_password(password)
admin.is_staff = True
admin.is_superuser = True
admin.save()
" || true

echo "==> [ERPangea] Populando dados de demonstração (se base estiver vazia)..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.contacts.models import Contact
if Contact.objects.count() == 0:
    from django.core.management import call_command
    print('Populando contatos base...')
    call_command('seed_contacts_50')
    print('Populando construtoras de Manaus...')
    call_command('seed_manaus_constructors')
    print('Populando propostas e contratos comerciais...')
    call_command('seed_commercial_demo')
" || true

echo "==> [ERPangea] Coletando arquivos estáticos para WhiteNoise..."
python manage.py collectstatic --noinput || true

echo "==> [ERPangea] Iniciando Gunicorn WSGI Server em 0.0.0.0:8000..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-4} --threads ${GUNICORN_THREADS:-2}
