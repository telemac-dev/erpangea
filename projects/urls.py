from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('novo/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/editar/', views.project_edit, name='project_edit'),
    path('tarefa/<int:pk>/status/', views.task_update_status, name='task_update_status'),
]
