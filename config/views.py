import json
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

def health_check(request):
    status = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown'
    }
    status_code = 200

    # 1. Checagem do Banco de Dados
    try:
        connection.ensure_connection()
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
        status_code = 503

    # 2. Checagem do Cache / Redis
    try:
        cache.set('health_test_key', 'ok', timeout=10)
        val = cache.get('health_test_key')
        if val == 'ok':
            status['cache'] = 'connected'
        else:
            status['cache'] = 'unexpected_response'
            status['status'] = 'unhealthy'
            status_code = 503
    except Exception as e:
        status['cache'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
        status_code = 503

    return JsonResponse(status, status=status_code)
