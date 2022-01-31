from django.shortcuts import render
from django.views.generic import ListView, CreateView

from contato.models import Contato


class ContatoListView(ListView):
    model = Contato
    context_object_name = "contatos"
    template_name="contato_list.html"


class ContatoCreateView(CreateView):
    model = Contato
    template_name = "contato_create.html"
    
