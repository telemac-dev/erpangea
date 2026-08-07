from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('nova/', views.bill_create, name='bill_create'),
    path('<int:pk>/', views.bill_detail, name='bill_detail'),
    path('<int:pk>/editar/', views.bill_edit, name='bill_edit'),
    path('relatorio/', views.payables_report, name='payables_report'),
]
