from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    path('', views.payable_list, name='list'),
    path('create/modal/', views.create_payable_modal, name='create_modal'),
    path('<int:pk>/approve/', views.approve_payable, name='approve'),
    path('<int:pk>/liquidate/modal/', views.liquidate_payable_modal, name='liquidate_modal'),
    path('project-report/<int:pk>/', views.project_profitability_report, name='project_report'),
]
