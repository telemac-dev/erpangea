import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('erpangea')

# Usa as configuracoes do settings.py que comecam com CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descoberta automatica de tasks em todas as apps instaladas
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Celery Heartbeat Request: {self.request!r}')
