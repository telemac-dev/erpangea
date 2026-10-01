from .context import set_current_request, reset_current_request

class AuditContextMiddleware:
    """
    Middleware thread-safe e async-safe baseado em ContextVars
    para captura do contexto da requisicao HTTP (usuario, IP, User-Agent).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = set_current_request(request)
        try:
            response = self.get_response(request)
        finally:
            reset_current_request(token)
        return response
