#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Uso: $0 <caminho_do_arquivo_backup.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"
CHECKSUM_FILE="${BACKUP_FILE}.sha256"

echo "==> [ERPangea] Iniciando processo de restauração de desastre..."

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Erro: Arquivo de backup não encontrado: ${BACKUP_FILE}"
    exit 1
fi

if [ -f "${CHECKSUM_FILE}" ]; then
    echo " -> Validando integridade criptográfica SHA256..."
    sha256sum -c "${CHECKSUM_FILE}"
fi

TMP_RESTORE=$(mktemp -d)
tar -xzf "${BACKUP_FILE}" -C "${TMP_RESTORE}"

# 1. Restaura banco
if [ -f "${TMP_RESTORE}/database.sqlite3" ]; then
    echo " -> Restaurando base de dados..."
    cp "${TMP_RESTORE}/database.sqlite3" db.sqlite3
fi

# 2. Restaura mídias
if [ -d "${TMP_RESTORE}/media" ]; then
    echo " -> Restaurando repositório de mídias..."
    rm -rf media
    cp -r "${TMP_RESTORE}/media" media
fi

rm -rf "${TMP_RESTORE}"
echo "==> [ERPangea] Restauração validada e concluída com sucesso!"
