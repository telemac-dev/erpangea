from django.urls import path

from pessoa.models import Pessoa
from .views import ListaPessoaView
from . import views


urlpatterns = [
    path('', ListaPessoaView.as_view(), name='pessoa.index'),
    path('novo/', views.inserir, name='pessoa.novo'),
    path('editar/<int:pessoa_pk>', views.editar, name='pessoa.editar'),
]
