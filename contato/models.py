from django.contrib.auth.models import User
from django.db import models


class CarimboTempoUsuarioMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='create_by')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='update_by')

    class Meta:
        abstract = True

    def created_updated(model, request):
        obj = model.objects.latest('pk')
        if obj.created_by is None:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()


class Marcador(models.Model):
    nome = models.CharField(max_length=100, blank=False, unique=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = "Marcador"
        verbose_name_plural = "Marcadores"

    def __str__(self):
        return self.nome


class Contato(CarimboTempoUsuarioMixin):
    
    TIPO_CONTATO = [
    ('PF', 'Pessoa Fisica'),
    ('PJ', 'Pessoa Juridica'),
    ]
    
    tipo_contato = models.CharField(max_length=2, choices=TIPO_CONTATO, default='PJ')
    contato_ativa = models.BooleanField(default=True)
    nome = models.CharField(max_length=100, blank=False) # Nome (PF), Razão Social (PJ) 
    apelido = models.CharField(max_length=100, blank=True) # Apelido (PF), Nome Fantasia (PJ)
    inscricao_federal = models.CharField(max_length=14, blank=True, null=True, unique=True) # CPF (PF), CNPJ (PJ)
    carga = models.CharField(max_length=50, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    site_web = models.CharField(max_length=100, blank=True)
    marcador = models.ManyToManyField(Marcador, blank=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"

    def __str__(self):
        return self.nome
 
    # metodo que envia o usuário na url após sucesso ao salvar o formulário 
    # def get_absolute_url(self):
    #     return reverse("contato.editar", kwargs={"pk": self.pk})


class Endereco(models.Model):
    contato = models.ForeignKey(Contato)
    cep = models.CharField(max_length=8)
    logradouro = models.CharField(max_length=80)
    numero = models.CharField(max_length=50)
    complemento = models.CharField(max_length=1000, blank=True, null=True)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    uf = models.CharField(max_length=2)

    def __str__(self):
        return self.cep

