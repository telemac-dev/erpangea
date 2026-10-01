from django.db import models


class PersonTypeEnum(models.TextChoices):
    PF = 'PF', 'Pessoa Física'
    PJ = 'PJ', 'Pessoa Jurídica'

class Contact(models.Model):
    tipo_pessoa = models.CharField(max_length=2, choices=PersonTypeEnum.choices, default=PersonTypeEnum.PJ)
    razao_social_nome = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True)
    cpf_cnpj = models.CharField(max_length=18, unique=True, db_index=True)
    inscricao_estadual = models.CharField(max_length=50, blank=True, null=True)
    inscricao_municipal = models.CharField(max_length=50, blank=True, null=True)
    
    # Usando JSONField ao invés de ArrayField caso seja rodado com SQLite localmente, 
    # mas o Postgres suporta perfeitamente. Vamos usar ArrayField como na especificação.
    classificacoes = models.JSONField(
        
        blank=True,
        default=list,
        help_text="Ex: LEAD, CLIENTE, FORNECEDOR, PARCEIRO, ORGAO_PUBLICO"
    )
    
    email_principal = models.EmailField(blank=True, null=True)
    telefone_principal = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome_fantasia or self.razao_social_nome

class Address(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='addresses')
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    is_obra = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.cidade}/{self.estado}"

class ContactPerson(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='contact_persons')
    nome = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    telefone_direto = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.contact.razao_social_nome})"
