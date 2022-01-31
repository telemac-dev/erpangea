from django.urls import path
from .views import ContatoListView, ContatoCreateView


urlpatterns = [
    path('', ContatoListView.as_view(), name='contato.index'),
    path('', ContatoCreateView.as_view(), name='contato.novo'),
]
