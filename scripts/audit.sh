#!/usr/bin/env bash
set -uo pipefail

PASS=0; FAIL=0

check() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$actual" == "$expected" ]]; then
        echo "  [OK] $desc"
        ((PASS++))
    else
        echo "  [FAIL] $desc (ожидалось: '$expected', получено: '$actual')"
        ((FAIL++))
    fi
}

echo "Аудит конфигурации: $(hostname -f), $(date '+%Y-%m-%d %H:%M')"

echo "[1] Служба SSH"
check "Вход от имени root запрещён" "no" "$(sudo sshd -T | awk '/^permitrootlogin/{print $2}')"
check "Парольная аутентификация отключена" "no" "$(sudo sshd -T | awk '/^passwordauthentication/{print $2}')"

# TODO 1: проверьте, что значение параметра port отлично от 22
ssh_port="$(sudo sshd -T | awk '/^port/{print $2}')"
is_non_default_port="no"
[[ "$ssh_port" != "22" && -n "$ssh_port" ]] && is_non_default_port="yes"
check "Порт службы SSH отличен от стандартного 22" "yes" "$is_non_default_port"

# TODO 2: проверьте, что значение параметра maxauthtries равно 3
check "Лимит попыток аутентификации (maxauthtries) равен 3" "3" "$(sudo sshd -T | awk '/^maxauthtries/{print $2}')"

echo "[2] Межсетевой экран"
check "Межсетевой экран активен" "active" "$(sudo ufw status | awk '/^Status:/{print $2}')"

# TODO 3: проверьте, что политика по умолчанию для входящего трафика равна deny
# источник данных: sudo ufw status verbose | grep Default
check "Политика по умолчанию для входящего трафика (incoming) - deny" "deny" "$(sudo ufw status verbose | awk '/Default:/{print $2}')"

echo "[3] Учётные записи"
awk -F: '$3>=1000 && $3<65534 {printf "  %s (uid=%s)\n",$1,$3}' /etc/passwd

echo "[4] Веб-сервер"
check "Служба Nginx активна" "active" "$(systemctl is-active nginx 2>/dev/null || echo inactive)"

nginx_syntax="ok"
sudo nginx -t >/dev/null 2>&1 || nginx_syntax="error"
check "Конфигурация Nginx синтаксически корректна" "ok" "$nginx_syntax"

cert_valid="valid"
openssl x509 -checkend 2592000 -noout -in /etc/ssl/certs/devops.crt >/dev/null 2>&1 || cert_valid="expired"
check "Сертификат TLS действителен не менее 30 дней" "valid" "$cert_valid"

web_perm="ok"
writable_files="$(find /var/www/devops-site -perm -o+w 2>/dev/null)"
key_mode="$(sudo stat -c '%a' /etc/ssl/private/devops.key 2>/dev/null || echo '')"
if [[ -n "$writable_files" || "$key_mode" != "600" ]]; then
    web_perm="insecure"
fi
check "Права веб-ресурса безопасны (нет o+w, ключ 600)" "ok" "$web_perm"

echo "Пройдено: $PASS, не пройдено: $FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
