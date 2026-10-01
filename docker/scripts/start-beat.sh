#!/bin/bash
set -e

LOG_LEVEL=${CELERY_LOG_LEVEL:-INFO}

echo "==> Iniciando Celery Beat Scheduler..."
exec celery -A config beat --loglevel=$LOG_LEVEL --scheduler=django_celery_beat.schedulers:DatabaseScheduler
