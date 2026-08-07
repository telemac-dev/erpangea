from django.contrib import admin
from .models import (
    Contato, TipoContato, ContatoTipo, PessoaFisica, PessoaJuridica,
    VinculoContato, Endereco, ContatoEndereco, ContatoTelefone, ContatoEmail,
    ContatoComercial, OrgaoPublico, Empreendimento
)

class PessoaFisicaInline(admin.StackedInline):
    model = PessoaFisica
    extra = 0

class PessoaJuridicaInline(admin.StackedInline):
    model = PessoaJuridica
    extra = 0

class ContatoTipoInline(admin.TabularInline):
    model = ContatoTipo
    extra = 0

class ContatoTelefoneInline(admin.TabularInline):
    model = ContatoTelefone
    extra = 0

class ContatoEmailInline(admin.TabularInline):
    model = ContatoEmail
    extra = 0

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome_razao_social', 'tipo_pessoa', 'ativo', 'created_at')
    list_filter = ('tipo_pessoa', 'ativo')
    search_fields = ('nome_razao_social', 'nome_fantasia', 'apelido')
    inlines = [PessoaFisicaInline, PessoaJuridicaInline, ContatoTipoInline, ContatoTelefoneInline, ContatoEmailInline]

@admin.register(TipoContato)
class TipoContatoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'descricao')

@admin.register(VinculoContato)
class VinculoContatoAdmin(admin.ModelAdmin):
    list_display = ('pessoa_fisica', 'pessoa_juridica', 'tipo_vinculo', 'cargo', 'ativo')
    list_filter = ('tipo_vinculo', 'ativo')

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('logradouro', 'numero', 'bairro', 'municipio', 'uf', 'cep')
    search_fields = ('logradouro', 'municipio', 'cep')

admin.site.register(PessoaFisica)
admin.site.register(PessoaJuridica)
admin.site.register(OrgaoPublico)
admin.site.register(Empreendimento)
admin.site.register(ContatoComercial)
