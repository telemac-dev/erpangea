from contextvars import ContextVar

_current_request = ContextVar('current_request', default=None)

def set_current_request(request):
    return _current_request.set(request)

def reset_current_request(token):
    _current_request.reset(token)

def get_current_request():
    return _current_request.get()

def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
