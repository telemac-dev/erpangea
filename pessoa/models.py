from django.db import models
from django.contrib.auth.models import User


class Pessoa(model.Model):

    TIPO_PESSOA = [
    ('PF', 'Pessoa Fisica'),
    ('PJ', 'Pessoa Juridica'),
    ]

    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='create')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='update')
    tipo_pessoa = models.
    pessoa_ativa = models.Boelean