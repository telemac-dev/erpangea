# Generated by Django 3.2.9 on 2022-01-31 19:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Marcador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Marcador',
                'verbose_name_plural': 'Marcadores',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Contato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tipo_contato', models.CharField(choices=[('PF', 'Pessoa Fisica'), ('PJ', 'Pessoa Juridica')], default='PJ', max_length=2)),
                ('contato_ativa', models.BooleanField(default=True)),
                ('nome', models.CharField(max_length=100)),
                ('apelido', models.CharField(blank=True, max_length=100)),
                ('inscricao_federal', models.CharField(blank=True, max_length=14, null=True, unique=True)),
                ('carga', models.CharField(blank=True, max_length=50)),
                ('telefone', models.CharField(blank=True, max_length=20)),
                ('Mobile', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=100)),
                ('site_web', models.CharField(blank=True, max_length=100)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='create_by', to=settings.AUTH_USER_MODEL)),
                ('marcador', models.ManyToManyField(to='contato.Marcador')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='update_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contato',
                'verbose_name_plural': 'Contatos',
                'ordering': ['nome'],
            },
        ),
    ]
