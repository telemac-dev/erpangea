from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Contact
from .forms import ContactForm

def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'contacts/list.html', {'contacts': contacts})

def create_contact_modal(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            # Retorna o header para fechar modal e recarregar ou um partial
            response = HttpResponse('Criado com sucesso.')
            response['HX-Refresh'] = 'true'
            return response

    return render(request, 'contacts/partials/create_modal.html', {'form': form})

def validate_document(request):
    if request.method == 'POST':
        cpf_cnpj = request.POST.get('cpf_cnpj', '').strip()
        if Contact.objects.filter(cpf_cnpj=cpf_cnpj).exists():
            return HttpResponse('<div class="text-danger">Este documento já está cadastrado.</div>')
        return HttpResponse('<div class="text-success">Documento válido e disponível.</div>')
    return HttpResponse('')
