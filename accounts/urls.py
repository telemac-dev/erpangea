from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Gestão de Usuários (Admin)
    path('gestao-usuarios/', views.user_list, name='user_list'),
    path('gestao-usuarios/<int:pk>/editar/', views.user_edit, name='user_edit'),
    path('gestao-usuarios/<int:pk>/status/', views.user_toggle_active, name='user_toggle_active'),
]
