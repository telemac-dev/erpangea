from django.contrib import admin
from pessoa.models import Endereco, Pessoa, Telefone


# Register your models here.
admin.site.register(Pessoa)
admin.site.register(Endereco)
admin.site.register(Telefone)