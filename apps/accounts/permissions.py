from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin

def user_has_sector(user, allowed_sectors):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    if profile and profile.sector in allowed_sectors:
        return True
    # Tambem verifica grupos Django caso pertença ao grupo correspondente
    if user.groups.filter(name__in=allowed_sectors).exists():
        return True
    return False

def role_required(*allowed_sectors):
    """
    Decorator para views baseadas em funcao garantindo acesso por setor corporativo.
    Exemplo: @role_required('TECNICO', 'TI')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            if not user_has_sector(request.user, allowed_sectors):
                raise PermissionDenied("Acesso não autorizado para o setor corporativo do usuário.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class RoleRequiredMixin(AccessMixin):
    """
    Mixin para CBVs exigindo um ou mais setores corporativos.
    Exemplo: allowed_sectors = ['FINANCEIRO', 'TI']
    """
    allowed_sectors = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not user_has_sector(request.user, self.allowed_sectors):
            raise PermissionDenied("Acesso não autorizado para o setor corporativo do usuário.")
        return super().dispatch(request, *args, **kwargs)
