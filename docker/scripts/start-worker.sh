#!/bin/bash
set -e

CONCURRENCY=${CELERY_WORKER_CONCURRENCY:-4}
LOG_LEVEL=${CELERY_LOG_LEVEL:-INFO}

echo "==> Iniciando Celery Worker (Concurrency: $CONCURRENCY, Level: $LOG_LEVEL)..."
exec celery -A config worker --loglevel=$LOG_LEVEL --concurrency=$CONCURRENCY
