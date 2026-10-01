from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Autenticacao basica
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('help/', views.AdminHelpView.as_view(), name='admin_help'),

    # Alteracao de Senha (Autenticado)
    path('password/change/', views.UserPasswordChangeView.as_view(), name='password_change'),

    # Recuperacao de Senha Esquecida (Publico)
    path('password/reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', views.UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
