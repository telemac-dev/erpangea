from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('nova/', views.invoice_create, name='invoice_create'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/registrar-pagamento/', views.invoice_register_payment, name='invoice_register_payment'),
    path('<int:pk>/editar/', views.invoice_edit, name='invoice_edit'),
]
