from django.urls import path
from . import views

app_name = 'measurements'

urlpatterns = [
    path('', views.measurement_list, name='list'),
    path('create/modal/', views.create_measurement_modal, name='create_modal'),
    path('<int:pk>/approve/', views.approve_measurement, name='approve'),
]
