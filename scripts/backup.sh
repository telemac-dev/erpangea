#!/usr/bin/env bash
set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
BACKUP_FILE="${BACKUP_DIR}/erpangea_backup_${TIMESTAMP}.tar.gz"

echo "==> [ERPangea] Iniciando rotina de backup..."

# Cria pasta temporária
TMP_DIR=$(mktemp -d)
mkdir -p "${TMP_DIR}/data"

# 1. Backup do Banco de Dados
if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "${TMP_DIR}/data/database.sqlite3"
    echo " -> Copiando banco de dados local SQLite..."
    
fi

# 2. Backup de Mídias (Projetos, EDMS, Anexos, Notas)
if [ -d "media" ]; then
    echo " -> Copiando arquivos de mídia do repositório..."
    cp -r media "${TMP_DIR}/data/"
else
    mkdir -p "${TMP_DIR}/data/media"
fi

# 3. Compactação e Checksum
echo " -> Compactando arquivo final..."
tar -czf "${BACKUP_FILE}" -C "${TMP_DIR}/data" .

sha256sum "${BACKUP_FILE}" > "${BACKUP_FILE}.sha256"

# Limpeza
rm -rf "${TMP_DIR}"

echo "==> [ERPangea] Backup finalizado com sucesso em: ${BACKUP_FILE}"
echo " -> Checksum SHA256: $(cat ${BACKUP_FILE}.sha256)"
