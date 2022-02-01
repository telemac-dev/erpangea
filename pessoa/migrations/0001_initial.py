# Generated by Django 3.2.9 on 2022-01-30 19:09

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
            name='Pessoa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tipo_pessoa', models.CharField(choices=[('PF', 'Pessoa Fisica'), ('PJ', 'Pessoa Juridica')], default='PJ', max_length=2)),
                ('pessoa_ativa', models.BooleanField(default=True)),
                ('nome', models.CharField(max_length=100)),
                ('apelido', models.CharField(blank=True, max_length=100)),
                ('inscricao_federal', models.CharField(blank=True, max_length=14, null=True, unique=True)),
                ('inscricao_estadual', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('data_nascimento', models.DateField(null=True)),
                ('email', models.EmailField(blank=True, max_length=100)),
                ('site_web', models.CharField(blank=True, max_length=100)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='create', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='update', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Telefone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marcador', models.CharField(choices=[('Principal', 'Principal'), ('Comercial', 'Comercial'), ('Casa', 'Casa'), ('Celular', 'Celular'), ('Wathsapp', 'Wathsapp')], default='Celular', max_length=20)),
                ('numero', models.CharField(max_length=20)),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='telefones', to='pessoa.pessoa')),
            ],
        ),
        migrations.CreateModel(
            name='Endereco',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cep', models.IntegerField(blank=True, null=True)),
                ('logradouro', models.CharField(max_length=100)),
                ('numero', models.CharField(max_length=5)),
                ('bairro', models.CharField(max_length=100)),
                ('cidade', models.CharField(max_length=100)),
                ('uf', models.CharField(max_length=2)),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enderecos', to='pessoa.pessoa')),
            ],
        ),
    ]
