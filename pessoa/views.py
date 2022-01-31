from django.forms import inlineformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView

from pessoa.forms import EnderecoForm, PessoaForm, TelefoneForm
from .models import Endereco, Pessoa, Telefone


class ListaPessoaView(ListView):
    model = Pessoa
    queryset = Pessoa.objects.all().order_by('nome')
    #queryset = Pessoa.objects.select_related('enderecos').select_related('telefones').all().order_by('nome')
    

def inserir(request):
    if request.method == "GET":
        form = PessoaForm()
        form_endereco_factory = inlineformset_factory(Pessoa, Endereco, form=EnderecoForm, extra=1)
        form_telefone_factory = inlineformset_factory(Pessoa, Telefone, form=TelefoneForm, extra=1)
        form_telefone = form_telefone_factory()
        form_endereco = form_endereco_factory()
        context = {
            'form': form,
            'form_telefone': form_telefone,
            'form_endereco': form_endereco,
        }
        return render(request, "pessoa/form.html", context)
    elif request.method == 'POST':
        form = PessoaForm(request.POST)
        form_telefone_factory = inlineformset_factory(Pessoa, Telefone, form=TelefoneForm)
        form_endereco_factory = inlineformset_factory(Pessoa, Endereco, form=EnderecoForm)
        form_telefone = form_telefone_factory(request.POST)
        form_endereco = form_endereco_factory(request.POST)
        if form.is_valid() and form_telefone.is_valid() and form_endereco.is_valid():
            pessoa = form.save()
            form_telefone.instance = pessoa
            form_endereco.instance = pessoa
            form_telefone.save()
            form_endereco.save()
            return redirect(reverse('pessoa.index'))
        else:
            context = {
                'form': form,
                'form_telefone': form_telefone,
                'form_endereco': form_endereco,
            }
            return render(request,'pessoa/form.html')

       
def editar(request, pessoa_pk):
    if request.method == "GET":
        objeto = Pessoa.objects.filter(id=pessoa_pk).first()
        if objeto is None:
            return redirect(reverse('pessoa.index'))
        form = PessoaForm(instance=objeto)
        
        extra_telefone = 1 if objeto.telefones.first() is None else 0
        extra_endereco = 1 if objeto.enderecos.first() is None else 0
        
        form_telefone_factory = inlineformset_factory(Pessoa, Telefone, form=TelefoneForm, extra=extra_telefone)
        form_endereco_factory = inlineformset_factory(Pessoa, Endereco, form=EnderecoForm, extra=extra_endereco)
        form_telefone = form_telefone_factory(instance=objeto)
        form_endereco = form_endereco_factory(instance=objeto)
        context = {
            'form': form,
            'form_telefone': form_telefone,
            'form_endereco': form_endereco,
        }
        return render(request, "pessoa/form.html", context)
    elif request.method == "POST":
        objeto = Pessoa.objects.filter(id=pessoa_pk).first()
        if objeto is None:
            return redirect(reverse('pessoa.index'))
        form = PessoaForm(request.POST, instance=objeto)
        form_telefone_factory = inlineformset_factory(Pessoa, Telefone, form=TelefoneForm)
        form_endereco_factory = inlineformset_factory(Pessoa, Endereco, form=EnderecoForm)
        form_telefone = form_telefone_factory(request.POST, instance=objeto)
        form_endereco = form_endereco_factory(request.POST, instance=objeto)
        if form.is_valid() and form_telefone.is_valid() and form_endereco.is_valid():
            pessoa = form.save()
            form_telefone.instance = pessoa
            form_endereco.instance = pessoa
            form_telefone.save()
            form_endereco.save()
            return redirect(reverse('pessoa.index'))
        else:
            context = {
                'form': form,
                'form_telefone': form_telefone,
                'form_endereco': form_endereco,
            }
            return render(request,'pessoa/form.html')
        
