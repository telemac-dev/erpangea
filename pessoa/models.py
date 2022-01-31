from django.db import models
from django.contrib.auth.models import User


class Pessoa(models.Model):

    TIPO_PESSOA = [
    ('PF', 'Pessoa Fisica'),
    ('PJ', 'Pessoa Juridica'),
    ]

    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='create')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='update')
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA, default='PJ')
    pessoa_ativa = models.BooleanField(default=True)
    nome = models.CharField(max_length=100, blank=False)
    apelido = models.CharField(max_length=100, blank=True)
    inscricao_federal = models.CharField(max_length=14, blank=True, null=True, unique=True)
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True, unique=True)
    data_nascimento = models.DateField(null=True)
    email = models.EmailField(max_length=100, blank=True)
    site_web = models.CharField(max_length=100, blank=True)
 
    
    # Metadados
    class Meta:
        ordering = ['nome']
    
    
    def __str__(self):
        """ String para representar o objeto MyModelName (no site Admin)."""
        return self.nome
    

class Endereco(models.Model):
    pessoa = models.ForeignKey('Pessoa', on_delete=models.CASCADE, related_name='enderecos')
    cep = models.IntegerField(blank=True, null=True)
    logradouro = models.CharField(max_length=100)
    numero = models.CharField(max_length=5)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    
    def __str__(self):
        return f'{self.logradouro}, {self.numero}\n{self.bairro}\n{self.cidade}\{self.uf}'
    
    
class Telefone(models.Model):
    
    TIPO_MARCADOR = (
        ('Principal', 'Principal'),
        ('Comercial', 'Comercial'),
        ('Casa', 'Casa'),
        ('Celular', 'Celular'),
        ('Wathsapp', 'Wathsapp'),
    )
    
    pessoa = models.ForeignKey('Pessoa', on_delete=models.CASCADE, related_name='telefones')
    marcador = models.CharField(max_length=20, choices=TIPO_MARCADOR, default='Celular')
    numero = models.CharField(max_length=20, blank=False)
    
    def __str__(self):
        return f'{self.marcador}: {self.numero}'
    
    