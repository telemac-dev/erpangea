import re
import json
import urllib.request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Contact, Interaction, ContactRole, PersonTypeChoices
from .forms import ContactForm, InteractionForm
from .utils import validate_cpf, validate_cnpj, format_cpf, format_cnpj, format_cep

@login_required
def contact_list(request):
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')

    contacts = Contact.objects.prefetch_related('roles').all()

    if query:
        contacts = contacts.filter(
            Q(name__icontains=query) |
            Q(trade_name__icontains=query) |
            Q(document__icontains=query) |
            Q(email__icontains=query)
        )

    if role_filter:
        contacts = contacts.filter(roles__name=role_filter)

    roles = ContactRole.objects.all()

    context = {
        'contacts': contacts,
        'query': query,
        'role_filter': role_filter,
        'roles': roles,
    }
    return render(request, 'contacts/contact_list.html', context)

@login_required
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f'Contato "{contact.name}" criado com sucesso!')
            return redirect('contact_detail', pk=contact.pk)
        else:
            messages.error(request, 'Erro ao salvar contato. Verifique os dados.')
    else:
        form = ContactForm()

    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Novo Contato'})

@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact.objects.prefetch_related('roles', 'interactions__user'), pk=pk)

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
    return render(request, 'contacts/contact_detail.html', context)

@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f'Contato "{contact.name}" atualizado com sucesso!')
            return redirect('contact_detail', pk=contact.pk)
        else:
            messages.error(request, 'Erro ao atualizar contato.')
    else:
        form = ContactForm(instance=contact)

    return render(request, 'contacts/contact_form.html', {'form': form, 'contact': contact, 'title': f'Editar {contact.name}'})

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        name = contact.name
        contact.delete()
        messages.success(request, f'Contato "{name}" removido com sucesso.')
        return redirect('contact_list')

    return render(request, 'contacts/contact_confirm_delete.html', {'contact': contact})

@login_required
def format_document_hx(request):
    """HTMX endpoint para formatação e validação dinâmica de CPF/CNPJ no evento on-blur."""
    document_raw = request.POST.get('document', '')
    person_type = request.POST.get('person_type', PersonTypeChoices.PJ)

    digits = re.sub(r'\D', '', str(document_raw))
    formatted_value = document_raw
    error_msg = None

    if digits:
        if person_type == PersonTypeChoices.PF:
            if not validate_cpf(digits):
                error_msg = 'CPF inválido. Informe um número de CPF válido com 11 dígitos (ex: 123.456.789-00).'
                formatted_value = digits
            else:
                formatted_value = format_cpf(digits)
        elif person_type == PersonTypeChoices.PJ:
            if not validate_cnpj(digits):
                error_msg = 'CNPJ inválido. Informe um número de CNPJ válido com 14 dígitos (ex: 12.345.678/0001-12).'
                formatted_value = digits
            else:
                formatted_value = format_cnpj(digits)

    context = {
        'value': formatted_value,
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
