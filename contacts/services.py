from django.db import transaction
from django.utils import timezone
from .models import (
    Contato, TipoPessoaChoices, TipoContato, ContatoTipo,
    PessoaFisica, PessoaJuridica, VinculoContato,
    Endereco, ContatoEndereco, ContatoTelefone, ContatoEmail,
    ContatoComercial, OrgaoPublico, Empreendimento,
    CodigoTipoContatoChoices
)
from .utils import format_cpf, format_cnpj, format_cep

@transaction.atomic
def create_contact(nome_razao_social, tipo_pessoa=TipoPessoaChoices.JURIDICA, user=None, **kwargs):
    """Cria um contato básico."""
    contato = Contato.objects.create(
        nome_razao_social=nome_razao_social,
        tipo_pessoa=tipo_pessoa,
        created_by=user,
        updated_by=user,
        **kwargs
    )
    return contato

@transaction.atomic
def create_pf_contact(nome_completo, cpf=None, email=None, telefone=None, user=None, roles=None, **pf_kwargs):
    """Cria uma Pessoa Física completa com papéis e canais de contato."""
    contato = create_contact(
        nome_razao_social=nome_completo,
        tipo_pessoa=TipoPessoaChoices.FISICA,
        user=user
    )
    
    formatted_cpf = format_cpf(cpf) if cpf else None
    pf = PessoaFisica.objects.create(
        contato=contato,
        cpf=formatted_cpf,
        email_pessoal=email or '',
        telefone_pessoal=telefone or '',
        **pf_kwargs
    )
    
    if email:
        add_email(contato, email=email, tipo='PESSOAL', principal=True)
    if telefone:
        add_telefone(contato, numero=telefone, tipo='CELULAR', principal=True)
        
    if roles:
        set_contact_roles(contato, roles)

    return contato

@transaction.atomic
def create_pj_contact(razao_social, cnpj=None, nome_fantasia='', email=None, telefone=None, user=None, roles=None, **pj_kwargs):
    """Cria uma Pessoa Jurídica completa com papéis e canais de contato."""
    contato = create_contact(
        nome_razao_social=razao_social,
        nome_fantasia=nome_fantasia,
        tipo_pessoa=TipoPessoaChoices.JURIDICA,
        user=user
    )
    
    formatted_cnpj = format_cnpj(cnpj) if cnpj else None
    pj = PessoaJuridica.objects.create(
        contato=contato,
        razao_social=razao_social,
        nome_fantasia=nome_fantasia,
        cnpj=formatted_cnpj,
        email_comercial=email or '',
        telefone_comercial=telefone or '',
        **pj_kwargs
    )
    
    if email:
        add_email(contato, email=email, tipo='COMERCIAL', principal=True, recebe_documentos=True)
    if telefone:
        add_telefone(contato, numero=telefone, tipo='COMERCIAL', principal=True)
        
    if roles:
        set_contact_roles(contato, roles)

    return contato

@transaction.atomic
def soft_delete_contact(contato, user=None):
    """Executa a exclusão lógica de um contato preservando seus registros históricos."""
    contato.deleted_at = timezone.now()
    contato.ativo = False
    contato.updated_by = user
    contato.save()
    return contato

@transaction.atomic
def set_contact_roles(contato, role_codes):
    """Define os papéis ativos de um contato."""
    for code in role_codes:
        tipo, _ = TipoContato.objects.get_or_create(codigo=code, defaults={'nome': code})
        ContatoTipo.objects.get_or_create(
            contato=contato,
            tipo_contato=tipo,
            defaults={'ativo': True, 'data_inicio': timezone.now().date()}
        )

@transaction.atomic
def add_endereco(contato, logradouro, municipio='', uf='', cep='', numero='', complemento='', bairro='', tipo_endereco='COMERCIAL', principal=True):
    """Adiciona um endereço a um contato."""
    formatted_cep = format_cep(cep) if cep else ''
    if principal:
        ContatoEndereco.objects.filter(contato=contato, principal=True).update(principal=False)
        
    end = Endereco.objects.create(
        logradouro=logradouro,
        numero=numero,
        complemento=complemento,
        bairro=bairro,
        cep=formatted_cep,
        municipio=municipio,
        uf=uf
    )
    
    ce = ContatoEndereco.objects.create(
        contato=contato,
        endereco=end,
        tipo_endereco=tipo_endereco,
        principal=principal
    )
    return ce

@transaction.atomic
def add_telefone(contato, numero, tipo='CELULAR', principal=True, whatsapp=False):
    """Adiciona um telefone ao contato."""
    if principal:
        ContatoTelefone.objects.filter(contato=contato, principal=True).update(principal=False)
    return ContatoTelefone.objects.create(
        contato=contato,
        numero=numero,
        tipo=tipo,
        principal=principal,
        whatsapp=whatsapp
    )

@transaction.atomic
def add_email(contato, email, tipo='COMERCIAL', principal=True, recebe_documentos=False, recebe_cobranca=False):
    """Adiciona um e-mail ao contato."""
    if principal:
        ContatoEmail.objects.filter(contato=contato, principal=True).update(principal=False)
    return ContatoEmail.objects.create(
        contato=contato,
        email=email.lower().strip(),
        tipo=tipo,
        principal=principal,
        recebe_documentos=recebe_documentos,
        recebe_cobranca=recebe_cobranca
    )

@transaction.atomic
def create_vinculo(pf_contato, pj_contato, tipo_vinculo='CONTATO_COMERCIAL', cargo='', departamento='', **kwargs):
    """Cria um vínculo entre uma Pessoa Física e uma Pessoa Jurídica."""
    if pf_contato.tipo_pessoa != TipoPessoaChoices.FISICA:
        raise ValueError("O contato de origem deve ser Pessoa Física.")
    if pj_contato.tipo_pessoa != TipoPessoaChoices.JURIDICA:
        raise ValueError("O contato de destino deve ser Pessoa Jurídica.")
        
    return VinculoContato.objects.create(
        pessoa_fisica=pf_contato,
        pessoa_juridica=pj_contato,
        tipo_vinculo=tipo_vinculo,
        cargo=cargo,
        departamento=departamento,
        **kwargs
    )
