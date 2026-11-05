#!/usr/bin/env bash
# Доставка статического ресурса на devops-vm
# Использование: scripts/deploy.sh [--dry-run]
set -euo pipefail

REMOTE="devops"
REMOTE_DIR="/var/www/devops-site/"
SITE_URL="https://devops.local"
CA_CERT="${HOME}/devops.crt"
if [[ ! -f "${CA_CERT}" && -f "/mnt/c/Users/frolo/devops.crt" ]]; then
    CA_CERT="/mnt/c/Users/frolo/devops.crt"
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
LOCAL_DIR="${REPO_ROOT}/site/"

# 1. Разбор аргумента --dry-run
DRY_RUN=false
if [[ $# -gt 0 ]]; then
    if [[ "$1" == "--dry-run" ]]; then
        DRY_RUN=true
    else
        echo "Ошибка: неизвестный аргумент '$1'" >&2
        echo "Использование: $0 [--dry-run]" >&2
        exit 1
    fi
fi

# 2. Проверки по требованиям 4 и 5
# Требование 4: Проверка наличия site/index.html
if [[ ! -f "${LOCAL_DIR}index.html" ]]; then
    echo "Ошибка: обязательный файл ${LOCAL_DIR}index.html не найден!" >&2
    exit 1
fi

# Требование 5: Проверка отсутствия незафиксированных изменений в репозитории
if [[ -n "$(git status --porcelain)" ]]; then
    echo "Ошибка: в репозитории имеются незафиксированные изменения!" >&2
    git status --short >&2
    exit 1
fi

# 3. Синхронизация каталога ${LOCAL_DIR} на ${REMOTE}:${REMOTE_DIR}
RSYNC_OPTS=(-avz --delete --chmod=D755,F644 -e "ssh -o BatchMode=yes -o ConnectTimeout=5")
if [[ "$DRY_RUN" == true ]]; then
    RSYNC_OPTS+=(--dry-run)
fi

rsync "${RSYNC_OPTS[@]}" "${LOCAL_DIR}" "${REMOTE}:${REMOTE_DIR}"

# 4. При --dry-run — завершение с кодом 0 без проверки доступности
if [[ "$DRY_RUN" == true ]]; then
    echo "Dry-run завершён успешно. План операций выведен, сервер не изменялся."
    exit 0
fi

# 5. Проверка доступности ${SITE_URL} и завершение с корректным кодом возврата
if ! curl -sf --cacert "${CA_CERT}" --resolve devops.local:443:127.0.0.1 "${SITE_URL}/" > /dev/null; then
    echo "Ошибка: ресурс ${SITE_URL} недоступен или не прошёл проверку сертификата!" >&2
    exit 1
fi

COMMIT_HASH="$(git rev-parse --short HEAD)"
echo "Деплой успешно выполнен. Доставлен коммит: ${COMMIT_HASH}"
exit 0
