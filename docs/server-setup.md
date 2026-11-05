# Конфигурация виртуальной машины devops-vm

Настоящий документ содержит спецификацию параметров и пошаговые команды для полного воспроизведения конфигурации целевого сервера `devops-vm` (включая сценарий быстрого восстановления после отката на снимок `01-clean-install`).

---

## 1. Параметры машины

| Параметр | Значение | Примечание |
| :--- | :--- | :--- |
| **Наименование ВМ** | `devops-vm` | Задается в Oracle VirtualBox |
| **Тип и версия ОС** | Linux / Ubuntu (64-bit) | Ubuntu Server 24.04 LTS (без GUI, не minimized) |
| **Оперативная память (RAM)** | 2048 МБ (2 ГБ) | Базовый объём для учебных сервисов |
| **Количество ядер процессора (vCPU)** | 2 | Минимально рекомендуемое для компиляции и сборки |
| **Дисковый накопитель** | 25 ГБ | VDI, динамически расширяемый |
| **Видеопамять** | 16 МБ | Графическая подсистема не используется |

---

## 2. Сетевые интерфейсы

| Адаптер | Тип подключения | Полученный IP-адрес | Назначение |
| :--- | :--- | :--- | :--- |
| **Адаптер 1 (enp0s3)** | NAT | `10.0.2.15/24` | Доступ гостевой ОС в интернет к внешним репозиториям пакетов; входящий доступ только через проброс портов VirtualBox |
| **Адаптер 2 (enp0s8)** | Виртуальный адаптер хоста (Host-only) | `192.168.56.101/24` *(или аналогичный из диапазона `192.168.56.0/24`)* | Прямой изолированный сетевой сегмент между хостом и ВМ; используется для прямого доступа к веб-серверу (в ПР № 6) и разрешения DNS |

---

## 3. Правило проброса портов (Port Forwarding)

Настроено в свойствах **Адаптера 1 (NAT)** VirtualBox:

| Наименование правила | Протокол | IP хоста | Порт хоста | IP гостя | Порт гостя | Статус |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ssh` (первоначальный) | TCP | `127.0.0.1` | `2222` | *(пусто)* | `22` | Использовался до переноса порта sshd |
| `ssh` (после hardening) | TCP | `127.0.0.1` | `2222` | *(пусто)* | `2222` | **Действующее правило**: проброс на нестандартный порт sshd |

---

## 4. Учётные записи

| Пользователь | UID | Группы | Назначение | Способ аутентификации |
| :--- | :--- | :--- | :--- | :--- |
| `root` | `0` | `root` | Суперпользователь ОС | Прямой вход по SSH запрещен (`PermitRootLogin no`) |
| `student` | `1000` | `student, adm, cdrom, sudo, dip, plugdev, lxd` | Пользователь начальной установки | Пароль (использовался для первичной инициализации) |
| `devops` | `1001` | `devops, sudo` | Основной административный пользователь | **Исключительно по SSH-ключу** Ed25519 (`~/.ssh/devops_vm.pub`), парольный вход заблокирован |

### Команды создания пользователя devops:
```bash
sudo adduser devops
sudo usermod -aG sudo devops
```

### Размещение ключа на сервере (в ~/.ssh/authorized_keys пользователя devops):
```bash
# На сервере:
sudo -u devops mkdir -p /home/devops/.ssh
sudo -u devops chmod 700 /home/devops/.ssh
sudo -u devops touch /home/devops/.ssh/authorized_keys
sudo -u devops chmod 600 /home/devops/.ssh/authorized_keys
# Добавление публичного ключа с хоста:
echo "ssh-ed25519 <ПУБЛИЧНЫЙ_КЛЮЧ> devops-vm-key" | sudo -u devops tee -a /home/devops/.ssh/authorized_keys
```

---

## 5. Служба SSH

* **Порт прослушивания**: `2222`
* **Файл основной конфигурации**: `/etc/ssh/sshd_config` (не модифицируется напрямую, создан бэкап `/etc/ssh/sshd_config.backup`)
* **Дополняющий файл конфигурации**: `/etc/ssh/sshd_config.d/99-hardening.conf`
* **Конфликтующие файлы**: В Ubuntu 24.04 в файле `/etc/ssh/sshd_config.d/50-cloud-init.conf` закомментирована директива `PasswordAuthentication yes`.

### Содержимое `/etc/ssh/sshd_config.d/99-hardening.conf`:
```text
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
PermitEmptyPasswords no
MaxAuthTries 3
LoginGraceTime 30
AllowUsers devops
X11Forwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
```

### Особенность сокетной активации в Ubuntu 24.04:
Для применения директивы `Port 2222` необходимо отключить socket activation и включить классический сервис:
```bash
sudo systemctl disable --now ssh.socket
sudo systemctl enable --now ssh.service
sudo systemctl restart ssh
```

---

## 6. Правила межсетевого экрана (UFW)

* **Политика по умолчанию для входящего трафика (`incoming`)**: `deny`
* **Политика по умолчанию для исходящего трафика (`outgoing`)**: `allow`
* **Статус**: `active`

### Список правил (`sudo ufw status verbose`):
```text
To                         Action      From
--                         ------      ----
2222/tcp (SSH rate-limited) LIMIT IN    Anywhere
80/tcp (HTTP)              ALLOW IN    Anywhere
443/tcp (HTTPS)            ALLOW IN    Anywhere
2222/tcp (v6)              LIMIT IN    Anywhere (v6)
80/tcp (v6)                ALLOW IN    Anywhere (v6)
443/tcp (v6)               ALLOW IN    Anywhere (v6)
```

### Команды воспроизведения UFW:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw limit 2222/tcp comment 'SSH rate-limited'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw enable
```

---

## 7. Снимки состояния (Snapshots)

| Снимок | Момент создания | Состояние системы |
| :--- | :--- | :--- |
| `01-clean-install` | Сразу после чистой установки Ubuntu Server 24.04 и обновления пакетов (`apt update && apt upgrade`) | Чистая ОС, пользователь `student`, SSH на стандартном порту 22. Точка восстановления для последующих практических работ. |
| `02-keys-configured` | После создания пользователя `devops`, генерации ключа Ed25519 и настройки `~/.ssh/config` | Пользователь `devops` создан и входит в группу `sudo`, проверен вход по ключу `ssh devops`. |
| `03-ssh-hardened` | После применения `99-hardening.conf`, смены порта на 2222, отключения `ssh.socket` и настройки UFW | SSH защищен (нет паролей, нет root, порт 2222), UFW активен с правилами `LIMIT 2222/tcp`, `ALLOW 80,443`. |

---

## 8. Процедура быстрого восстановления (Cheat-Sheet за 5 минут)

При откате на снимок `01-clean-install`:
1. Подключиться: `ssh student@127.0.0.1 -p 2222` (убедиться, что в настройках ВМ порт гостя временно 22).
2. Создать пользователя: `sudo adduser --disabled-password --gecos "" devops && sudo usermod -aG sudo devops`
3. Скопировать открытый ключ в `/home/devops/.ssh/authorized_keys` с правами `700` на каталог и `600` на файл.
4. Создать `/etc/ssh/sshd_config.d/99-hardening.conf` с параметрами выше, отключить `50-cloud-init.conf`.
5. Выполнить:
   ```bash
   sudo systemctl disable --now ssh.socket
   sudo systemctl enable --now ssh.service
   sudo systemctl restart ssh
   ```
6. В VirtualBox сменить проброс порта гостя с 22 на 2222.
7. Настроить UFW:
   ```bash
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw limit 2222/tcp comment 'SSH rate-limited'
   sudo ufw allow 80/tcp comment 'HTTP'
   sudo ufw allow 443/tcp comment 'HTTPS'
   sudo ufw --force enable
   ```
8. Запустить `scripts/audit.sh` и убедиться в получении `0 FAIL`.


---

## 8. Веб-сервер Nginx

| Параметр | Значение / Путь | Примечание |
| :--- | :--- | :--- |
| **Устанавливаемый пакет** | `nginx` (`nginx-common`) | Установка через `apt install -y nginx` |
| **Путь к конфигурации ресурса** | `/etc/nginx/sites-available/devops-site` | Символическая ссылка в `/etc/nginx/sites-enabled/` |
| **Стандартный ресурс** | `/etc/nginx/sites-enabled/default` | Отключён (символическая ссылка удалена) |
| **Каталог веб-ресурса** | `/var/www/devops-site` | Владелец `devops:devops`, права `755` на каталоги, `644` на файлы |
| **Путь к сертификату TLS** | `/etc/ssl/certs/devops.crt` | Права `644`, владелец `root:root` |
| **Путь к закрытому ключу TLS** | `/etc/ssl/private/devops.key` | Права `600`, владелец `root:root` |
| **Срок действия сертификата** | 365 дней (1 год) | Самоподписанный с расширением SAN `DNS:devops.local` |

### Команда выпуска сертификата:
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/devops.key \
  -out /etc/ssl/certs/devops.crt \
  -subj "/CN=devops.local" \
  -addext "subjectAltName=DNS:devops.local"
```

### Конфигурация виртуального хоста `/etc/nginx/sites-available/devops-site`:
```nginx
# Блок 1: перенаправление HTTP -> HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name devops.local;
    return 301 https://$host$request_uri;
}

# Блок 2: основной виртуальный хост HTTPS
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name devops.local;
    root /var/www/devops-site;
    index index.html;

    ssl_certificate /etc/ssl/certs/devops.crt;
    ssl_certificate_key /etc/ssl/private/devops.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        try_files $uri $uri/ =404;
    }

    error_page 404 /404.html;
    access_log /var/log/nginx/devops-site.access.log;
    error_log /var/log/nginx/devops-site.error.log;
}
```
