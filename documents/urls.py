from django.urls import path
from . import views

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('novo/', views.document_create, name='document_create'),
    path('<int:pk>/', views.document_detail, name='document_detail'),
    path('<int:pk>/editar/', views.document_edit, name='document_edit'),
]
