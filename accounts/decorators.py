from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, 'Acesso negado. Apenas Administradores podem acessar esta página.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_manager:
            messages.error(request, 'Acesso negado. Requer perfil de Gerente ou Administrador.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def financial_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.can_access_financials:
            messages.error(request, 'Acesso negado. Seu perfil de acesso não tem permissão para visualizar dados financeiros.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
