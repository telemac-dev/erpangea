from django.urls import path
from .views import ContatoListView, ContatoCreateView, ContatoUpdateView, ContatoDeleteView


urlpatterns = [
    path('', ContatoListView.as_view(), name='contato.index'),
    path('novo/', ContatoCreateView.as_view(), name='contato.novo'),
    path('editar/<int:pk>', ContatoUpdateView.as_view(), name='contato.editar'),
    path('remover/<int:pk>', ContatoDeleteView.as_view(), name='contato.remover'),
]
