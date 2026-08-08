import re
import json
import urllib.request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Contato, Interaction, TipoContato, TipoPessoaChoices
from .forms import ContactForm, InteractionForm
from .utils import validate_cpf, validate_cnpj, format_cpf, format_cnpj, format_cep
from .services import soft_delete_contact

@login_required
def contact_list(request):
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')

    contacts = Contato.objects.filter(deleted_at__isnull=True)

    if query:
        contacts = contacts.filter(
            Q(nome_razao_social__icontains=query) |
            Q(nome_fantasia__icontains=query) |
            Q(pessoa_fisica__cpf__icontains=query) |
            Q(pessoa_juridica__cnpj__icontains=query) |
            Q(emails__email__icontains=query) |
            Q(telefones__numero__icontains=query) |
            Q(enderecos__endereco__municipio__icontains=query)
        ).distinct()

    if role_filter:
        contacts = contacts.filter(papeis_rel__tipo_contato__codigo=role_filter, papeis_rel__ativo=True)

    roles = TipoContato.objects.all()

    context = {
        'contacts': contacts,
        'query': query,
        'role_filter': role_filter,
        'roles': roles,
    }
    return render(request, 'contacts/lista.html', context)

@login_required
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.created_by = request.user
            contact.updated_by = request.user
            contact.save()
            form.save(commit=True)
            messages.success(request, f'Contato "{contact.nome_razao_social}" criado com sucesso!')
            return redirect('contact_detail', pk=contact.pk)
        else:
            messages.error(request, 'Erro ao salvar contato. Verifique os dados.')
    else:
        form = ContactForm()

    return render(request, 'contacts/formulario.html', {'form': form, 'title': 'Novo Contato'})

@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(
        Contato.objects.filter(deleted_at__isnull=True)
        .prefetch_related('interactions__user', 'papeis_rel__tipo_contato', 'enderecos__endereco', 'telefones', 'emails'), 
        pk=pk
    )

    if request.method == 'POST':
        interaction_form = InteractionForm(request.POST)
        if interaction_form.is_valid():
            interaction = interaction_form.save(commit=False)
            interaction.contact = contact
            interaction.user = request.user
            interaction.save()
            messages.success(request, 'Interação registrada com sucesso!')
            return redirect('contact_detail', pk=contact.pk)
        else:
            messages.error(request, 'Erro ao registrar interação.')
    else:
        interaction_form = InteractionForm()

    context = {
        'contact': contact,
        'interactions': contact.interactions.all(),
        'interaction_form': interaction_form,
    }
    return render(request, 'contacts/detalhe.html', context)

@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(Contato, pk=pk)

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.updated_by = request.user
            contact.save()
            form.save(commit=True)
            messages.success(request, f'Contato "{contact.nome_razao_social}" atualizado com sucesso!')
            return redirect('contact_detail', pk=contact.pk)
        else:
            messages.error(request, 'Erro ao atualizar contato.')
    else:
        form = ContactForm(instance=contact)

    return render(request, 'contacts/formulario.html', {'form': form, 'contact': contact, 'title': f'Editar {contact.nome_razao_social}'})

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contato, pk=pk)
    if request.method == 'POST':
        name = contact.nome_razao_social
        soft_delete_contact(contact, user=request.user)
        messages.success(request, f'Contato "{name}" removido com sucesso.')
        return redirect('contact_list')
    return render(request, 'contacts/confirmar_exclusao.html', {'contact': contact})

@login_required
def format_document_hx(request):
    """HTMX endpoint para formatação e validação dinâmica de CPF/CNPJ no evento on-blur."""
    document_raw = request.POST.get('document', '')
    person_type = request.POST.get('person_type', TipoPessoaChoices.JURIDICA)

    digits = re.sub(r'\D', '', str(document_raw))
    formatted_value = document_raw
    error_msg = None

    if digits:
        if person_type == TipoPessoaChoices.FISICA or person_type == 'PF':
            if not validate_cpf(digits):
                error_msg = 'CPF inválido. Informe um número de CPF válido com 11 dígitos (ex: 123.456.789-00).'
                formatted_value = digits
            else:
                formatted_value = format_cpf(digits)
        elif person_type == TipoPessoaChoices.JURIDICA or person_type == 'PJ':
            if not validate_cnpj(digits):
                error_msg = 'CNPJ inválido. Informe um número de CNPJ válido com 14 dígitos (ex: 12.345.678/0001-12).'
                formatted_value = digits
            else:
                formatted_value = format_cnpj(digits)

    context = {
        'value': formatted_value,
        'person_type': person_type,
        'error_msg': error_msg,
    }
    return render(request, 'contacts/partials/document_field.html', context)

@login_required
def lookup_cep_hx(request):
    """HTMX endpoint para consultar o CEP no ViaCEP e preencher os campos de endereço no evento on-blur."""
    zip_code_raw = request.POST.get('zip_code', '')
    address = request.POST.get('address', '')
    city = request.POST.get('city', '')
    state = request.POST.get('state', '')

    digits = re.sub(r'\D', '', str(zip_code_raw))
    formatted_zip = format_cep(digits) if digits else zip_code_raw
    error_msg = None

    if len(digits) == 8:
        url = f"https://viacep.com.br/ws/{digits}/json/"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'ERPangea/1.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('erro') or data.get('erro') == 'true' or data.get('erro') is True:
                    error_msg = 'CEP não encontrado.'
                else:
                    logradouro = data.get('logradouro', '')
                    bairro = data.get('bairro', '')
                    localidade = data.get('localidade', '')
                    uf = data.get('uf', '')

                    address_parts = [p for p in [logradouro, bairro] if p]
                    address = " - ".join(address_parts) if address_parts else address
                    city = localidade or city
                    state = uf or state
        except Exception:
            error_msg = 'Não foi possível consultar o ViaCEP.'
    elif digits and len(digits) != 8:
        error_msg = 'CEP inválido. Informe um CEP com 8 dígitos (ex: 01001-000).'

    context = {
        'zip_code': formatted_zip,
        'address': address,
        'city': city,
        'state': state,
        'error_msg': error_msg,
    }
    return render(request, 'contacts/partials/address_fields.html', context)
@login_required
def related_company_hx(request):
    """HTMX endpoint para exibir ou ocultar o campo de Empresa Relacionada dinamicamente ao alterar o Tipo de Pessoa."""
    person_type = request.POST.get('person_type') or request.GET.get('person_type') or TipoPessoaChoices.JURIDICA
    form = ContactForm(initial={'person_type': person_type})
    context = {
        'form': form,
        'person_type': person_type,
    }
    return render(request, 'contacts/partials/_related_company_field.html', context)
@login_required
def add_vinculo_modal_hx(request):
    """HTMX endpoint para exibir modal e cadastrar vinculo de membro da equipe."""
    contact_id = request.GET.get('contact_id') or request.POST.get('contact_id')
    
    if request.method == 'POST':
        nome_membro = request.POST.get('nome_membro', '')
        cpf_membro = request.POST.get('cpf_membro', '')
        cargo = request.POST.get('cargo', '')
        email_membro = request.POST.get('email_membro', '')
        telefone_membro = request.POST.get('telefone_membro', '')
        tipo_vinculo = request.POST.get('tipo_vinculo', 'CONTATO_COMERCIAL')

        if nome_membro:
            pf_contato = create_pf_contact(
                nome_completo=nome_membro,
                cpf=cpf_membro,
                email=email_membro,
                telefone=telefone_membro,
                user=request.user
            )
            
            if contact_id:
                pj_contato = get_object_or_404(Contato, pk=contact_id)
                create_vinculo(
                    pf_contato=pf_contato,
                    pj_contato=pj_contato,
                    cargo=cargo,
                    tipo_vinculo=tipo_vinculo,
                    email_corporativo=email_membro,
                    telefone_corporativo=telefone_membro
                )
                messages.success(request, f'Membro "{nome_membro}" adicionado com sucesso!')

        vinculos = []
        if contact_id:
            pj_contato = get_object_or_404(Contato, pk=contact_id)
            vinculos = pj_contato.vinculos_como_pj.filter(ativo=True)
            
        return render(request, 'contacts/partials/_vinculos_grid.html', {
            'vinculos': vinculos,
            'contact_id': contact_id,
        })

    return render(request, 'contacts/partials/_vinculo_modal_form.html', {
        'contact_id': contact_id,
    })
