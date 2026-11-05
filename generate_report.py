import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

doc = Document()

# Set standard margins (2 cm)
for section in doc.sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

# Styles
def set_font(run, name="Times New Roman", size=Pt(12), bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color

def add_p(doc, text="", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6, bold=False, italic=False, size=Pt(12)):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if text:
        run = p.add_run(text)
        set_font(run, size=size, bold=bold, italic=italic)
    return p

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.8)
    cell = tbl.cell(0, 0)
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F4F5F7"/>')
    cell._tc.get_or_add_tcPr().append(shading)
    
    # borders
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
            <w:left w:val="single" w:sz="18" w:space="0" w:color="0052CC"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
        </w:tcBorders>
    ''')
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(code_text)
    set_font(run, name="Consolas", size=Pt(9.5), color=RGBColor(20, 20, 20))
    add_p(doc, "", space_after=4)

# ----------------- ТИТУЛЬНЫЙ ЛИСТ -----------------
add_p(doc, "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ", WD_ALIGN_PARAGRAPH.CENTER, 0, 2, bold=True, size=Pt(10))
add_p(doc, "ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ", WD_ALIGN_PARAGRAPH.CENTER, 0, 2, size=Pt(9))
add_p(doc, "«МИРЭА — Российский технологический университет»", WD_ALIGN_PARAGRAPH.CENTER, 0, 2, bold=True, size=Pt(11))
add_p(doc, "Институт перспективных технологий и индустриального программирования (ИПТИП)", WD_ALIGN_PARAGRAPH.CENTER, 0, 2, size=Pt(10))
add_p(doc, "Кафедра индустриального программирования", WD_ALIGN_PARAGRAPH.CENTER, 0, 24, size=Pt(10))

add_p(doc, "ОТЧЁТ", WD_ALIGN_PARAGRAPH.CENTER, 36, 6, bold=True, size=Pt(18))
add_p(doc, "по практической работе № 5", WD_ALIGN_PARAGRAPH.CENTER, 0, 6, bold=True, size=Pt(14))
add_p(doc, "«Удалённый сервер и безопасный доступ. SSH, sudo, UFW, DNS»", WD_ALIGN_PARAGRAPH.CENTER, 0, 12, bold=True, italic=True, size=Pt(13))
add_p(doc, "Дисциплина: Инструменты DevOps (DevOps-практикум)", WD_ALIGN_PARAGRAPH.CENTER, 0, 60, size=Pt(12))

p_info = add_p(doc, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=80)
run_info = p_info.add_run(
    "Выполнил: студент группы ИКБО\n"
    "Фролов Кирилл\n\n"
    "Преподаватель:\n"
    "Гиматдинов Дамир Маратович\n"
)
set_font(run_info, size=Pt(11))

add_p(doc, "Москва, 2026", WD_ALIGN_PARAGRAPH.CENTER, 40, 0, size=Pt(11))
doc.add_page_break()

# ----------------- 1. ЦЕЛЬ И ЗАДАЧИ РАБОТЫ -----------------
add_p(doc, "1. Цель и задачи работы", bold=True, size=Pt(14), space_before=12, space_after=8)
p = add_p(doc)
p.add_run("Цель работы: ").bold = True
p.add_run("Формирование практических навыков первичной защиты удалённого сервера под управлением операционной системы семейства Linux (Ubuntu Server 24.04 LTS).")

add_p(doc, "Для достижения поставленной цели решены следующие задачи:", space_after=4)
tasks = [
    "а) Развёрнута виртуальная машина под управлением Ubuntu Server 24.04 LTS и настроена сетевая связность (NAT + Host-only);",
    "б) Изучена модель доверия протокола SSH, включая назначение ключа хоста, механизм ключевой аутентификации клиента и роль файлов known_hosts и authorized_keys;",
    "в) Выполнено базовое усиление защиты (hardening) SSH-сервера при сохранении непрерывности управляющего доступа (смена порта, отключение паролей, отключение root);",
    "г) Настроен межсетевой экран UFW в соответствии с принципом «запрещено всё, что не разрешено явно», с ограничением интенсивности подключений (rate-limiting);",
    "д) Сопоставлено серверу локальное доменное имя и изучен порядок разрешения имён в операционной системе Linux."
]
for t in tasks:
    add_p(doc, t, space_after=2)

# ----------------- 2. ХОД ВЫПОЛНЕНИЯ РАБОТЫ -----------------
add_p(doc, "2. Пошаговое выполнение работы", bold=True, size=Pt(14), space_before=16, space_after=8)

# 2.1 Подготовка
add_p(doc, "2.1. Развёртывание и подготовка виртуальной машины", bold=True, size=Pt(12), space_before=8, space_after=4)
add_p(doc, "В среде виртуализации Oracle VM VirtualBox развёрнута виртуальная машина devops-vm со следующими характеристиками:")
add_p(doc, "• ОЗУ: 2048 МБ, 2 vCPU, Диск: 25 ГБ (динамический VDI).")
add_p(doc, "• Адаптер 1 (NAT): настроен проброс портов Хост 127.0.0.1:2222 -> Гость 22 (впоследствии изменён на 2222).")
add_p(doc, "• Адаптер 2 (Host-only): подключен к VirtualBox Host-Only Ethernet Adapter (подсеть 192.168.56.0/24).")
add_p(doc, "• ОС: Ubuntu Server 24.04 LTS, пользователь student, установлен компонент OpenSSH Server.")

add_p(doc, "После завершения установки проверены сетевые интерфейсы командой ip -brief address:")
add_code_block(doc, "$ ip -brief address\nlo               UNKNOWN        127.0.0.1/8 ::1/128 \nenp0s3           UP             10.0.2.15/24 metric 100\nenp0s8           UP             192.168.56.102/24 metric 100")

# Embed screenshot if exists
if os.path.exists("images/report_01_ip_brief_address.png"):
    add_p(doc, "Рис. 1. Вывод команды ip -brief address на виртуальной машине", italic=True, size=Pt(10), align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_picture("images/report_01_ip_brief_address.png", width=Inches(6.2))
    add_p(doc, "", space_after=8)

add_p(doc, "Создан контрольный снимок состояния виртуальной машины 01-clean-install.")

# 2.2 Задание 1
add_p(doc, "2.2. Задание 1. Учётная запись и ключевая аутентификация", bold=True, size=Pt(12), space_before=12, space_after=4)
add_p(doc, "1. На сервере создан отдельный административный пользователь devops, добавленный в группу sudo:")
add_code_block(doc, "sudo adduser devops\nsudo usermod -aG sudo devops\ngroups devops\n# Результат: devops : devops sudo users")

add_p(doc, "2. На хостовой системе сформирована отдельная ключевая пара по алгоритму Ed25519:")
add_code_block(doc, "ssh-keygen -t ed25519 -C \"devops-vm-key\" -f ~/.ssh/devops_vm")

add_p(doc, "3. Открытый ключ размещён на сервере в каталоге /home/devops/.ssh/authorized_keys, установлены строгие права доступа:")
add_code_block(doc, "chmod 700 ~/.ssh\nchmod 600 ~/.ssh/authorized_keys\nstat -c '%a %n' ~/.ssh ~/.ssh/authorized_keys\n# Результат: 700 /home/devops/.ssh\n#            600 /home/devops/.ssh/authorized_keys")

add_p(doc, "4. На хостовой системе настроен файл конфигурации клиента ~/.ssh/config:")
add_code_block(doc, "Host devops\n    HostName 127.0.0.1\n    Port 2222\n    User devops\n    IdentityFile ~/.ssh/devops_vm\n    IdentitiesOnly yes")

add_p(doc, "5. Зафиксированы методы аутентификации до усиления защиты службы:")
add_code_block(doc, "$ ssh -vvv -i ~/.ssh/devops_vm -p 2222 devops@127.0.0.1 2>&1 | grep -i \"authentications that can continue\"\ndebug1: Authentications that can continue: publickey,password")

add_p(doc, "Создан снимок состояния 02-keys-configured.")

# 2.3 Задание 2
add_p(doc, "2.3. Задание 2. Усиление защиты службы SSH", bold=True, size=Pt(12), space_before=12, space_after=4)
add_p(doc, "Создан дополняющий файл конфигурации /etc/ssh/sshd_config.d/99-hardening.conf:")
add_code_block(doc, "Port 2222\nPermitRootLogin no\nPasswordAuthentication no\nPubkeyAuthentication yes\nPermitEmptyPasswords no\nMaxAuthTries 3\nLoginGraceTime 30\nAllowUsers devops\nX11Forwarding no\nClientAliveInterval 300\nClientAliveCountMax 2")

add_p(doc, "В файле 50-cloud-init.conf закомментирована директива PasswordAuthentication yes во избежание переопределения. В связи с сокетной активацией в Ubuntu 24.04 служба переведена на классический юнит:")
add_code_block(doc, "sudo systemctl disable --now ssh.socket\nsudo systemctl enable --now ssh.service\nsudo systemctl restart ssh\nsudo ss -tlnp | grep sshd\n# Результат: LISTEN 0 128 0.0.0.0:2222")

add_p(doc, "В свойствах VirtualBox порт гостя для правила NAT изменён с 22 на 2222. Проведены контрольные проверки:")
add_code_block(doc, "# 1. Вход под devops по ключу: УСПЕХ\n$ ssh devops\n\n# 2. Попытка входа под root: ОТКАЗ\n$ ssh -p 2222 root@127.0.0.1\nroot@127.0.0.1: Permission denied (publickey).\n\n# 3. Попытка входа с отключенным ключом: ОТКАЗ\n$ ssh -p 2222 -o PubkeyAuthentication=no devops@127.0.0.1\ndevops@127.0.0.1: Permission denied (publickey).\n\n# 4. Методы аутентификации после hardening:\ndebug1: Authentications that can continue: publickey")

add_p(doc, "Запись в системном журнале:")
add_code_block(doc, "devops-vm sshd-session[3191]: Connection reset by invalid user root 10.0.2.2 port 58410 [preauth]")

add_p(doc, "Письменное объяснение различия диагностических сообщений:", bold=True)
add_p(doc, "• Для пользователя root сервер сразу отклоняет вход на этапе пре-аутентификации ([preauth]), так как директива PermitRootLogin no запрещает даже начало согласования учётных данных для суперпользователя. В журнале он помечается как invalid user.\n• При попытке входа пользователя devops с опцией PubkeyAuthentication=no клиент запрашивает альтернативные методы аутентификации (пароль), но поскольку директива PasswordAuthentication no отключила пароли, сервер возвращает пустой список разрешённых методов, кроме publickey, что приводит к немедленному завершению сессии с Permission denied (publickey).")

add_p(doc, "Создан снимок состояния 03-ssh-hardened.")

# 2.4 Задание 3
add_p(doc, "2.4. Задание 3. Конфигурирование межсетевого экрана (UFW)", bold=True, size=Pt(12), space_before=12, space_after=4)
add_p(doc, "Настроен брандмауэр UFW по принципу «запрещено всё, что не разрешено явно», с ограничением частоты подключений на порту 2222:")
add_code_block(doc, "sudo ufw default deny incoming\nsudo ufw default allow outgoing\nsudo ufw limit 2222/tcp comment 'SSH rate-limited'\nsudo ufw allow 80/tcp comment 'HTTP'\nsudo ufw allow 443/tcp comment 'HTTPS'\nsudo ufw logging medium\nsudo ufw --force enable")

add_p(doc, "Действующий статус UFW:")
add_code_block(doc, "Status: active\nLogging: on (medium)\nDefault: deny (incoming), allow (outgoing), disabled (routed)\n\nTo                         Action      From\n--                         ------      ----\n2222/tcp                   LIMIT IN    Anywhere                   # SSH rate-limited\n80/tcp                     ALLOW IN    Anywhere                   # HTTP\n443/tcp                    ALLOW IN    Anywhere                   # HTTPS")

add_p(doc, "Инициировано соединение с хоста на закрытый порт 8080 (curl.exe -m 3 http://127.0.0.1:8080), зафиксирована блокировка в журнале ядра /var/log/ufw.log:")
add_code_block(doc, "kernel: [UFW BLOCK] IN=enp0s3 OUT= MAC=08:00:27:41:d9:54:52:55:0a:00:02:02:08:00 SRC=10.0.2.2 DST=10.0.2.15 LEN=44 TOS=0x00 PREC=0x00 TTL=64 ID=210 PROTO=TCP SPT=61284 DPT=8080 WINDOW=65535 RES=0x00 SYN URGP=0")

add_p(doc, "Письменный разбор полей записи журнала UFW BLOCK:", bold=True)
add_p(doc, "• SRC=10.0.2.2 — IP-адрес источника пакета (Source IP). Адрес шлюза NAT VirtualBox, транслирующего запрос хостовой системы.\n• DST=10.0.2.15 — IP-адрес получателя (Destination IP). Адрес сетевого адаптера виртуальной машины enp0s3.\n• PROTO=TCP — протокол транспортного уровня (Transmission Control Protocol).\n• DPT=8080 — порт назначения (Destination Port). Закрытый порт 8080, трафик к которому заблокирован политикой default deny incoming.")

# 2.5 Задание 4
add_p(doc, "2.5. Задание 4. Локальное доменное имя", bold=True, size=Pt(12), space_before=12, space_after=4)
add_p(doc, "1. На хостовой системе настроен псевдоним devops.local для быстрого подключения по SSH.")
add_p(doc, "2. На сервере задано полное доменное имя (FQDN):")
add_code_block(doc, "sudo hostnamectl set-hostname devops-vm\nsudo sed -i 's/^127.0.1.1.*/127.0.1.1 devops-vm.devops.local devops-vm/' /etc/hosts\nhostname -f\n# Результат: devops-vm.devops.local")

# 2.6 Задание 5
add_p(doc, "2.6. Факультативное задание. Туннелирование средствами SSH", bold=True, size=Pt(12), space_before=12, space_after=4)
add_p(doc, "На сервере поднят HTTP-сервер, слушающий исключительно локальную петлю 127.0.0.1:8080:")
add_code_block(doc, "mkdir -p ~/restricted && cd ~/restricted\necho '<h1>Ресурс доступен только через туннель</h1>' > index.html\npython3 -m http.server 8080 --bind 127.0.0.1")

add_p(doc, "С хостовой системы поднят локальный SSH-туннель: ssh -L 9090:127.0.0.1:8080 -N devops.")
add_p(doc, "Обращение к http://localhost:9090 вернуло HTML-страницу сервиса.")
add_p(doc, "Обоснование:", bold=True)
add_p(doc, "Трафик передавался через разрешённый порт 2222 внутри зашифрованного сессионного канала SSH. Демон sshd на сервере распаковывает туннелированные данные и передаёт их сервису локально через интерфейс lo (обратная петля). Межсетевой экран UFW фильтрует входящие физические пакеты, поэтому локальный обмен внутри петли 127.0.0.1 не блокируется.")

# 2.7 Задание 6
add_p(doc, "2.7. Скрипт аудита конфигурации (scripts/audit.sh)", bold=True, size=Pt(12), space_before=12, space_after=4)
add_p(doc, "Разработан скрипт аудита scripts/audit.sh с реализацией всех трех TODO-блоков. Проведено двойное тестирование (на штатной и нарушенной конфигурациях):")
add_code_block(doc, "=== ТЕСТ 1: ШТАТНАЯ КОНФИГУРАЦИЯ ===\nАудит конфигурации: devops-vm.devops.local\n[1] Служба SSH\n  [OK] Вход от имени root запрещён\n  [OK] Парольная аутентификация отключена\n  [OK] Порт службы SSH отличен от стандартного 22\n  [OK] Лимит попыток аутентификации (maxauthtries) равен 3\n[2] Межсетевой экран\n  [OK] Межсетевой экран активен\n  [OK] Политика по умолчанию для входящего трафика (incoming) - deny\n[3] Учётные записи\n  student (uid=1000)\n  devops (uid=1001)\nПройдено: 6, не пройдено: 0 (код возврата: 0)\n\n=== ТЕСТ 2: НАРУШЕННАЯ КОНФИГУРАЦИЯ (MaxAuthTries 10) ===\n  [FAIL] Лимит попыток аутентификации (maxauthtries) равен 3 (ожидалось: '3', получено: '10')\nПройдено: 5, не пройдено: 1 (код возврата: 1)")

doc.add_page_break()

# ----------------- 3. ОТВЕТЫ НА КОНТРОЛЬНЫЕ ВОПРОСЫ -----------------
add_p(doc, "3. Ответы на контрольные вопросы (Раздел 7)", bold=True, size=Pt(14), space_before=12, space_after=8)

answers = [
    ("1. Чем обусловлена невозможность входящего соединения с гостевой системой при использовании адаптера типа NAT и возможность такового при использовании адаптера типа Host-only?",
     "При NAT гипервизор выступает маршрутизатором с трансляцией сетевых адресов. ВМ находится во внутренней изолированной подсети 10.0.2.0/24. Внешний хост не имеет маршрута к этой подсети, а в таблице трансляции NAT нет сопоставлений для инициативных входящих соединений (требуется явный Port Forwarding).\nПри Host-only создаётся общий L2/L3-сегмент (виртуальный коммутатор), в котором хост и гостевая система находятся в одной подсети (192.168.56.0/24), что позволяет адресовать гостевую систему напрямую без трансляции адресов."),

    ("2. Каково назначение файлов ~/.ssh/known_hosts и ~/.ssh/authorized_keys? На какой из систем размещается каждый из них?",
     "• ~/.ssh/known_hosts — размещается на клиенте (хостовой системе). Служит для аутентификации сервера клиентом (содержит открытые ключи серверов для предотвращения атак Man-in-the-Middle).\n• ~/.ssh/authorized_keys — размещается на сервере (гостевой системе). Служит для аутентификации клиента сервером (содержит список доверенных открытых ключей пользователей, которым разрешён вход)."),

    ("3. Обоснуйте преимущество аутентификации по ключу перед парольной с учётом того, что оба типа учётных данных передаются по защищённому каналу.",
     "1) Закрытый ключ никогда не передаётся по сети — аутентификация строится на криптографическом механизме «вызов-ответ» (challenge-response), где клиент подписывает случайный вызов сервера.\n2) Криптографическая стойкость: длина ключа (Ed25519 — 256 бит, RSA — 4096 бит) делает математически невозможным подбор полным перебором (brute-force), в отличие от пользовательских паролей.\n3) Утечка данных с сервера не раскрывает закрытый ключ клиента."),

    ("4. В чём состоит различие действий ufw allow и ufw limit?",
     "• ufw allow — безусловно пропускает весь входящий трафик на указанный порт.\n• ufw limit — реализует защиту от атак перебора паролей (rate-limiting): если с одного IP-адреса фиксируется 6 и более попыток установки соединения в течение 30 секунд, UFW временно блокирует пакеты с этого адреса."),

    ("5. Ошибка администратора при редактировании sshd_config и две команды для исключения отказа:",
     "• Нарушение процедуры: Администратор разорвал действующую сессию управления до проверки новой конфигурации через параллельное соединение в соседнем терминале, а также не выполнил синтаксическую проверку конфига до перезапуска службы.\n• Команды исключения: 1) sudo sshd -t (синтаксический контроль конфигурации); 2) Проверка подключения ssh devops в параллельном терминале без закрытия текущей сессии."),

    ("6. Результат выполнения: ufw default deny incoming, ufw enable, ufw allow 22/tcp:",
     "• Результат: Разрыв действующей SSH-сессии и полная потеря удалённого доступа к серверу.\n• Команда наступления: ufw enable, так как брандмауэр активировался с запретом всех входящих пакетов до добавления разрешающего правила для SSH.\n• Корректный порядок: 1) ufw default deny incoming; 2) ufw default allow outgoing; 3) ufw allow 22/tcp (или 2222/tcp); 4) ufw enable."),

    ("7. Изменён порт на 2222, выполнена команда sudo ufw allow ssh, соединение не работает:",
     "• Источник: Системная база соответствия служб и портов IANA — файл /etc/services. В нём за именем ssh закреплён порт 22/tcp. Команда сформировала правило для порта 22, а не 2222."),

    ("8. Оценка тезиса «Изменение порта службы SSH — security through obscurity»:",
     "• Тезис верен лишь отчасти. Смена порта не защищает от целенаправленной атаки (порт легко сканируется nmap за секунды).\n• Решаемая задача: Отсекается 99% фонового автоматизированного шума (ботнеты и скрипт-кидди, брутфорсящие стандартный 22 порт), что разгружает auth.log и экономит процессорные ресурсы.\n• Нерешаемая задача: Защита уязвимостей в самом OpenSSH от направленного взлома квалифицированным нарушителем."),

    ("9. Предупреждение REMOTE HOST IDENTIFICATION HAS CHANGED:",
     "• Три причины: 1) Штатная переустановка сервера (генерация новых ключей хоста); 2) Смена IP-адреса целевого узла; 3) Атака типа Man-in-the-Middle.\n• Разграничение: Администратор обязан внеполосным каналом (через консоль ВМ) проверить отпечаток открытого ключа (sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub) и сверить его с предъявляемым клиентом.\n• Почему ssh-keygen -R вслепую некорректен: Если имела место реальная атака подмены узла, удаление записи отключает защитный механизм и отдаёт учётные данные злоумышленнику."),

    ("10. Контроль прав доступа клиента к файлу закрытого ключа (600/700):",
     "• Причина: Клиент принудительно проверяет права доступа к закрытому ключу (~/.ssh — 700, id_ed25519 — 600).\n• Защита от угроз: Защищает от несанкционированного чтения закрытого ключа другими локальными пользователями и непривилегированными процессами в многопользовательской операционной системе."),

    ("11. ping myapp.local работает, а dig myapp.local возвращает пустой ответ:",
     "• Отсутствие противоречия: ping использует функцию getaddrinfo(), проверяющую порядок источников в /etc/nsswitch.conf (где первым указан файл /etc/hosts). Утилита dig является специализированным DNS-клиентом и обращается исключительно к серверам DNS по протоколу UDP/53, полностью игнорируя локальный файл /etc/hosts.\n• Порядок разрешения имён в Linux: 1) Файл /etc/hosts; 2) Локальный резолвер systemd-resolved (127.0.0.53); 3) Внешние DNS-серверы провайдера / DHCP."),

    ("12. Команда ssh -L 9090:127.0.0.1:8080 user@server и межсетевой экран:",
     "• Адресное пространство: Адрес 127.0.0.1 в целевой части интерпретируется в адресном пространстве целевого сервера (remote server).\n• Почему UFW не блокирует: Внешний сетевой трафик передаётся исключительно через разрешённый порт SSH (2222/tcp). Серверный демон sshd сам принимает этот трафик и локально пересылает на 127.0.0.1:8080 через локальную петлю (интерфейс lo), которую UFW по умолчанию не фильтрует."),

    ("13. Регистрация команд sudo и выполнение sudo su -:",
     "• Оценка: Мера недостаточна. При выполнении sudo su - фиксируется только запуск оболочки root. Все последующие команды администратора выполняются внутри интерактивного root-шелла и в auth.log не протоколируются.\n• Устранение: Запретить вызов интерактивных оболочек через sudoers, либо использовать подсистему расширенного аудита ядра Linux (auditd) для протоколирования системных вызовов execve с фиксацией исходного auid пользователя."),

    ("14. Три недостатка ручного конфигурирования (по сравнению с Ansible):",
     "1) Отсутствие воспроизводимости и масштабируемости (дрифт конфигураций при росте числа узлов);\n2) Отсутствие версионирования инфраструктуры (Infrastructure as Code) и невозможность быстрого отката;\n3) Отсутствие идемпотентности (повторный запуск команд приводит к дублированию строк и ошибкам).")
]

for q, a in answers:
    add_p(doc, q, bold=True, size=Pt(11), space_before=8, space_after=2)
    add_p(doc, a, size=Pt(11), space_after=6)

# ----------------- 4. ВЫВОДЫ -----------------
doc.add_page_break()
add_p(doc, "4. Выводы", bold=True, size=Pt(14), space_before=12, space_after=8)
add_p(doc, "В ходе выполнения практической работы № 5 были успешно освоены ключевые принципы и инструменты обеспечения базовой безопасности удалённого сервера под управлением Linux:")
add_p(doc, "1. Настроена двухсетевая топология (NAT + Host-only), обеспечивающая одновременно выход гостевой ОС в глобальную сеть и надёжный изолированный доступ хоста к учебным ресурсам.")
add_p(doc, "2. Реализована модель строгой аутентификации: вход суперпользователя root и парольная аутентификация полностью запрещены, настроен доступ администратора devops по эллиптическим ключам Ed25519.")
add_p(doc, "3. Служба OpenSSH перенесена на нестандартный порт 2222 с корректным отключением подсистемы сокетной активации systemd (ssh.socket) и устранением переопределения директив в конфигурациях cloud-init.")
add_p(doc, "4. Настроен межсетевой экран UFW с реализацией rate-limiting для предотвращения брутфорс-атак и детальным журналированием блокировок.")
add_p(doc, "5. Разработан и протестирован скрипт автоматизированного контроля конфигурации audit.sh, подтвердивший 100% соответствие развёрнутой системы критериям безопасности.")
add_p(doc, "Все контрольные точки сохранены в снимках состояния (01-clean-install, 02-keys-configured, 03-ssh-hardened), документация и скрипты зафиксированы в репозитории devops-course-2026 согласно стандарту Conventional Commits.")

doc.save("Отчет_Практическая_работа_5_Фролов.docx")
print("Report successfully generated!")
