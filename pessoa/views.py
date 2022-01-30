from django.shortcuts import render
from django.views.generic import ListView
from .models import Pessoa


class ListaPessoaView(ListView):
    model = Pe
