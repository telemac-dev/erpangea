from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin
from .models import HierarchyLevel, SectorChoices

def has_role(user, sector, min_level=HierarchyLevel.OPERACIONAL):
    """
    Avalia se o usuario autenticado possui o setor com nivel >= min_level.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.has_sector_permission(sector, min_level=min_level)

def require_role(sector_or_rules, min_level=HierarchyLevel.OPERACIONAL):
    """
    Decorator para views garantindo autorizacao cumulativa hierarquica.
    Suporta:
      1) Setor unico com nivel minimo:
         @require_role(SectorChoices.FINANCEIRO, min_level=HierarchyLevel.COORDENACAO)
      2) Lista de combinacoes alternativas (OR logico):
         @require_role([
             (SectorChoices.FINANCEIRO, HierarchyLevel.COORDENACAO),
             (SectorChoices.TI, HierarchyLevel.OPERACIONAL)
         ])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            authorized = False

            if isinstance(sector_or_rules, (list, tuple)) and sector_or_rules and isinstance(sector_or_rules[0], (list, tuple)):
                # Lista de regras (sector, min_level)
                for sec, lvl in sector_or_rules:
                    if has_role(request.user, sec, lvl):
                        authorized = True
                        break
            else:
                # Regra individual
                sec = sector_or_rules
                authorized = has_role(request.user, sec, min_level)

            if not authorized:
                raise PermissionDenied(
                    "Acesso negado: seu perfil não possui a alçada ou setor corporativo necessário para esta operação."
                )
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class RoleRequiredMixin(AccessMixin):
    """
    Mixin para CBVs com autorizacao cumulativa hierarquica.
    Exemplo:
        required_sector = SectorChoices.TECNICO
        min_level = HierarchyLevel.COORDENACAO
    """
    required_sector = None
    min_level = HierarchyLevel.OPERACIONAL
    alternative_roles = None # Lista de tuplas [(sector, min_level), ...]

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        authorized = False
        if self.alternative_roles:
            for sec, lvl in self.alternative_roles:
                if has_role(request.user, sec, lvl):
                    authorized = True
                    break
        elif self.required_sector:
            authorized = has_role(request.user, self.required_sector, self.min_level)
        elif request.user.is_superuser:
            authorized = True

        if not authorized:
            raise PermissionDenied(
                "Acesso negado: seu perfil não possui a alçada ou setor corporativo necessário para esta operação."
            )
        return super().dispatch(request, *args, **kwargs)
