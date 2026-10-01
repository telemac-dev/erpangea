#!/bin/bash
set -e

# Funcao de espera para o PostgreSQL
wait_for_postgres() {
    echo "==> Aguardando PostgreSQL em ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
    python << END
import sys
import time
import socket

host = "${POSTGRES_HOST:-db}"
port = int("${POSTGRES_PORT:-5432}")

start_time = time.time()
while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("==> PostgreSQL disponivel!")
            break
    except OSError:
        if time.time() - start_time > 60:
            print("==> Timeout esperando pelo PostgreSQL.", file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
END
}

# Funcao de espera para o Redis
wait_for_redis() {
    echo "==> Aguardando Redis em ${REDIS_HOST:-redis}:${REDIS_PORT:-6379}..."
    python << END
import sys
import time
import socket

host = "${REDIS_HOST:-redis}"
port = int("${REDIS_PORT:-6379}")

start_time = time.time()
while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("==> Redis disponivel!")
            break
    except OSError:
        if time.time() - start_time > 60:
            print("==> Timeout esperando pelo Redis.", file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
END
}

# Executa checagem se variaveis estiverem definidas
if [ "$USE_SQLITE" != "True" ] && [ -n "$POSTGRES_HOST" ]; then
    wait_for_postgres
fi

if [ -n "$REDIS_HOST" ]; then
    wait_for_redis
fi

exec "$@"
