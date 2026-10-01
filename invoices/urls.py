from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.invoice_list, name='list'),
    path('create/modal/', views.create_invoice_modal, name='create_modal'),
    path('<int:pk>/cancel/', views.cancel_invoice, name='cancel'),
]
