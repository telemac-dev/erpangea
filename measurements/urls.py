from django.urls import path
from . import views

urlpatterns = [
    path('', views.measurement_list, name='measurement_list'),
    path('nova/', views.measurement_create, name='measurement_create'),
    path('<int:pk>/', views.measurement_detail, name='measurement_detail'),
    path('<int:pk>/aprovar/', views.measurement_approve, name='measurement_approve'),
    path('<int:pk>/editar/', views.measurement_edit, name='measurement_edit'),
]
