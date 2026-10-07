# Отчёт о развёртывании и проверке защищённости системы StudentTrack

**Дата:** 01.10.2026

## 1. Инфраструктура

Система развёрнута на двух виртуальных машинах (VirtualBox, внутренняя сеть 192.168.56.0/24):

| Узел | Адрес | Назначение | Доступ |
|---|---|---|---|
| app-server | 192.168.56.10 | Веб-приложение StudentTrack (Flask + gunicorn, порт 5000) | SSH, пользователь `test` |
| db-server | 192.168.56.11 | PostgreSQL 18, база `diary` | SSH, пользователь `prod` |

Приложение работает под системным пользователем `diary` из каталога `/opt/diary`,
управляется службой systemd `diary.service`. Конфигурация — `/etc/diary/diary.env`:

```
DATABASE_URL=postgresql://diary_app:***@192.168.56.11:5432/diary
```

---

## 2. Создание пользователя с правами администратора

Задача: создать пользователя с правами администратора на сайте http://192.168.56.10:5000/.

### Действия

1. Подключение к app-server по SSH:

```bash
ssh test@192.168.56.10
```

2. Обнаружена штатная CLI-команда приложения (`/opt/diary/app/commands.py`):

```bash
flask create-admin <username> <email> --password <пароль>
```

Команда проверяет уникальность username/email, требует пароль не короче 8 символов,
сохраняет пароль в виде хеша (`set_password`, Werkzeug) и присваивает роль `admin`.

3. Создание администратора от имени системного пользователя `diary` с боевым окружением:

```bash
sudo -u diary bash -c '
  set -a; . /etc/diary/diary.env; set +a
  cd /opt/diary/app
  /opt/diary/venv/bin/flask --app run.py create-admin administrator administrator@example.com --password <пароль>
'
# Вывод: Администратор administrator создан.
```

Имя `admin` оказалось занято (существующий пользователь с ролью `student`), поэтому выбрано имя `administrator`.

4. Проверка записи в базе на db-server:

```bash
ssh prod@192.168.56.11
sudo -u postgres psql -d diary -c "SELECT username, email, role FROM users ORDER BY created_at;"
```

```
   username    |           email           |  role
---------------+---------------------------+---------
 mra           | mra@mra.ru                | student
 admin         | admin@example.com         | student
 administrator | administrator@example.com | admin
```

5. Проверка входа через сайт:

```bash
curl -c cookies.txt -X POST http://192.168.56.10:5000/login \
  --data-urlencode "identifier=administrator" \
  --data-urlencode "password=<пароль>"
# HTTP 302 Found, Location: /dashboard — вход успешен
curl -b cookies.txt http://192.168.56.10:5000/dashboard
# <title>Панель управления — StudentTrack</title>
```

**Итог:** логин `administrator`, роль `admin`, вход проверен.

---

## 3. Проверка на защите

### 3.1. Процесс, порт и журналы средствами Linux

**App-server:**

```bash
# Процесс
ps -eo user,pid,cmd | grep [g]unicorn
# diary 857 /opt/diary/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 run:app (+2 worker)

# Порт
sudo ss -tlnp | grep :5000
# LISTEN 0 2048 0.0.0.0:5000 users:(("gunicorn",pid=857,...))

# Служба и журналы
systemctl status diary --no-pager
sudo journalctl -u diary -n 8 --no-pager
```

**Db-server:**

```bash
ps -eo user,pid,cmd | grep [p]ostgres
# postgres 1009 /usr/lib/postgresql/18/bin/postgres -D /var/lib/postgresql/18/main ...

sudo ss -tlnp | grep :5432
# LISTEN 127.0.0.1:5432
# LISTEN 192.168.56.11:5432     ← только localhost и адрес внутренней сети

systemctl status postgresql --no-pager
sudo journalctl -u postgresql -n 6 --no-pager
```

### 3.2. Остановка БД и диагностика состояния приложения

1. Остановка базы на db-server:

```bash
sudo systemctl stop postgresql
systemctl is-active postgresql   # inactive
```

2. Диагностика приложения (app-server):

```bash
systemctl is-active diary        # active — процесс не падает
curl -o /dev/null -w '%{http_code}' http://192.168.56.10:5000/login     # 200 (страница не требует БД)
curl -o /dev/null -w '%{http_code}' -X POST http://192.168.56.10:5000/login \
  --data-urlencode identifier=administrator --data-urlencode password=***  # 500
```

3. Причина видна в журнале:

```bash
sudo journalctl -u diary --since '2 min ago' | grep -iE 'error|refus|connect'
# ERROR in app: Exception on /login [POST]
# psycopg2.OperationalError: SSL connection has been closed unexpectedly
```

**Вывод:** при недоступной БД приложение остаётся запущенным, отдаёт HTTP 500 на операции,
требующие БД; ошибка однозначно диагностируется в журнале службы.

4. Восстановление:

```bash
sudo systemctl start postgresql
systemctl is-active postgresql   # active
curl -i -X POST http://192.168.56.10:5000/login --data-urlencode ... 
# HTTP 302 Found, Location: /dashboard — вход восстановлен без перезапуска приложения
```

### 3.3. Изменение параметра службы с последующим восстановлением

Изменён параметр `TimeoutStopSec` (время ожидания корректной остановки) в `/etc/systemd/system/diary.service`:

```bash
systemctl show diary -p TimeoutStopUSec
# TimeoutStopUSec=30s                     ← исходное значение

sudo sed -i 's/^TimeoutStopSec=30/TimeoutStopSec=60/' /etc/systemd/system/diary.service
sudo systemctl daemon-reload

systemctl show diary -p TimeoutStopUSec
# TimeoutStopUSec=1min                    ← изменение применено
```

Восстановление:

```bash
sudo sed -i 's/^TimeoutStopSec=60/TimeoutStopSec=30/' /etc/systemd/system/diary.service
sudo systemctl daemon-reload
systemctl show diary -p TimeoutStopUSec   # TimeoutStopUSec=30s
systemctl is-active diary                 # active
curl -o /dev/null -w '%{http_code}' http://127.0.0.1:5000/login   # 200
```

Приложение во время изменения не останавливалось (достаточно `daemon-reload`).

### 3.4. Проверка сетевой недоступности БД с постороннего узла

Попытка подключения к порту 5432 с посторонней машины (не app-server):

```bash
(echo > /dev/tcp/192.168.56.11/5432)   # таймаут — порт недоступен
```

Защита настроена в три независимых уровня:

1. **PostgreSQL слушает только нужные адреса** (`/etc/postgresql/18/main/postgresql.conf`):

```
listen_addresses = 'localhost,192.168.56.11'
```

2. **pg_hba.conf** — единственная разрешённая сетевая строка:

```
host  diary  diary_app  192.168.56.10/32  scram-sha-256
```

Только пользователь `diary_app`, только база `diary`, только с адреса app-server, пароль по scram-sha-256.

3. **Файрвол ufw** на db-server:

```bash
sudo ufw status verbose
# Status: active
# Default: deny (incoming), allow (outgoing)
# 22/tcp   ALLOW IN  Anywhere
# 5432/tcp ALLOW IN  192.168.56.10
```

**Вывод:** с любого узла, кроме app-server, порт БД недоступен уже на уровне файрвола;
даже при обходе файрвола аутентификацию не пройти из-за pg_hba.

### 3.5. Перезагрузка обеих машин и проверка автоматического запуска

1. Перезагрузка обеих ВМ:

```bash
ssh prod@192.168.56.11 'sudo reboot'
ssh test@192.168.56.10 'sudo reboot'
```

2. Проверка после загрузки (обе службы `enabled` и поднялись автоматически):

```bash
# db-server
systemctl is-active postgresql    # active
systemctl is-enabled postgresql   # enabled
ss -tln | grep :5432              # LISTEN 127.0.0.1:5432, 192.168.56.11:5432

# app-server
systemctl is-active diary         # active
systemctl is-enabled diary        # enabled
ss -tln | grep :5000              # LISTEN 0.0.0.0:5000
sudo journalctl -u diary -b | head -4
# systemd[1]: Started diary.service - Diary application.
# gunicorn[862]: Listening at: http://0.0.0.0:5000
```

3. Сквозная проверка после перезагрузки:

```bash
curl -o /dev/null -w '%{http_code}' http://192.168.56.10:5000/login   # 200
curl -i -X POST http://192.168.56.10:5000/login \
  --data-urlencode identifier=administrator --data-urlencode password=***
# HTTP 302 Found, Location: /dashboard
curl -b cookies.txt http://192.168.56.10:5000/dashboard
# <title>Панель управления — StudentTrack</title>
```

**Вывод:** обе службы настроены на автозапуск (`enabled`) и успешно стартуют после
перезагрузки; система полностью работоспособна без ручного вмешательства.

---

## 4. Общий вывод

| Проверка | Результат |
|---|---|
| Создание администратора | ✅ `administrator`, роль `admin`, вход проверен |
| Процесс, порт, журналы | ✅ gunicorn/5000 и postgres/5432 найдены, журналы читаются через journalctl |
| Остановка БД | ✅ приложение живо, HTTP 500, причина видна в журнале, восстановление без перезапуска |
| Изменение параметра службы | ✅ `TimeoutStopSec` изменён и восстановлен, служба не прерывалась |
| Недоступность БД извне | ✅ ufw + listen_addresses + pg_hba — доступ только с app-server |
| Перезагрузка и автозапуск | ✅ обе службы `enabled`, стартуют автоматически, вход работает |

Система развёрнута корректно: приложение отделено от БД, доступ к базе ограничен
на уровнях сети, файрвола и аутентификации, службы управляются systemd и
восстанавливаются автоматически.
