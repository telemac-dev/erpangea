import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from apps.audit_log.models import AuditLog

@login_required
def dashboard_view(request):
    recent_logs = AuditLog.objects.select_related('user').all()[:15]
    total_audit_entries = AuditLog.objects.count()
    return render(request, 'dashboard.html', {
        'recent_logs': recent_logs,
        'total_audit_entries': total_audit_entries,
    })

def health_check(request):
    status = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown'
    }
    status_code = 200

    try:
        connection.ensure_connection()
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
        status_code = 503

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
