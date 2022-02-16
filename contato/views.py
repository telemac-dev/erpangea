from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Contato


class ContatoListView(ListView):
    model = Contato
    queryset = Contato.objects.all().order_by('nome')
    context_object_name = "contatos"
    template_name = "contato_list.html"


class ContatoCreateView(CreateView):
    model = Contato
    fields = ['tipo_contato', 'nome', 'apelido', 'inscricao_federal', 'carga', 'telefone', 'mobile', 'email', 'site_web', 'marcador']
    template_name = "contato/contato_create.html"
    success_url = "/contatos/"
    

class ContatoUpdateView(UpdateView):
    model = Contato
    fields = '__all__'
    template_name = "contato/contato_create.html"
    success_url = "/contatos/"


class ContatoDeleteView(DeleteView):
    model = Contato
    #success_url = reverse_lazy("contato.index")
    success_url = "/contatos/"
