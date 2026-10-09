# StudentTrack

StudentTrack — веб-приложение на Flask для учёта успеваемости, расписания и управления пользователями учебного заведения.

Система хранит информацию о студентах, учебных группах, дисциплинах, учебных планах, оценках, расписании занятий, а также реализует регистрацию, авторизацию и разграничение прав доступа по ролям через веб-интерфейс и HTTP API.

## Возможности

- работа с учебными группами, студентами, дисциплинами и учебными планами (CRUD);
- управление оценками с проверкой принадлежности дисциплины учебному плану группы и диапазона оценки (1–5);
- управление расписанием занятий с проверкой пересечений по времени, дню недели и учебному плану группы;
- регистрация и авторизация пользователей (по username или email), безопасное хеширование паролей;
- ролевая модель доступа: `student`, `teacher`, `admin`;
- личный кабинет студента: свои дисциплины, расписание, оценки;
- административная панель управления пользователями и назначением ролей;
- веб-интерфейс (dashboard) на Flask/Jinja2 с динамическим обновлением данных через JavaScript;
- HTTP API в формате JSON;
- единый формат обработки ошибок;
- health-check приложения с идентификатором экземпляра;
- хранение данных в PostgreSQL;
- контейнеризация через Docker и Docker Compose: Nginx-балансировщик, два экземпляра приложения, изолированная сеть, ограничения ресурсов, автоматическая проверка окружения (`make container-check`);
- автоматические тесты (pytest) и статический анализ кода (flake8).

## Технологии

- Python 3.13
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- Flask-Migrate / Alembic
- PostgreSQL 16 (драйвер psycopg 3)
- Gunicorn
- Nginx (обратный прокси и балансировщик)
- Werkzeug (хеширование паролей)
- python-dotenv
- Jinja2, HTML/CSS, JavaScript (fetch API)
- Docker, Docker Compose
- pytest, pytest-cov, pytest-xdist, flake8
- Git, GitHub (feature-branch workflow, Pull Request)

## Структура проекта

```text
diary/
|-- app/
|   |-- __init__.py
|   |-- config.py
|   |-- commands.py
|   |-- errors.py
|   |-- extensions.py
|   |-- permissions.py
|   |
|   |-- models/
|   |   |-- __init__.py
|   |   |-- group.py
|   |   |-- student.py
|   |   |-- discipline.py
|   |   |-- study_plan.py
|   |   |-- grade.py
|   |   |-- schedule.py
|   |   \-- user.py
|   |
|   |-- routes/
|   |   |-- __init__.py
|   |   |-- health.py
|   |   |-- groups.py
|   |   |-- students.py
|   |   |-- disciplines.py
|   |   |-- study_plans.py
|   |   |-- grades.py
|   |   |-- schedules.py
|   |   |-- auth.py
|   |   |-- me.py
|   |   |-- admin.py
|   |   \-- web.py
|   |
|   |-- services/
|   |   |-- group_service.py
|   |   \-- student_service.py
|   |
|   |-- static/
|   |   |-- css/style.css
|   |   \-- js/dashboard.js
|   |
|   \-- templates/
|       |-- base.html
|       |-- login.html
|       |-- register.html
|       \-- dashboard.html
|
|-- migrations/
|   |-- env.py
|   \-- versions/
|
|-- nginx/
|   \-- nginx.conf
|
|-- scripts/
|   |-- backup.py
|   |-- restore.py
|   |-- verify.py
|   \-- container_check.py
|
|-- backups/
|-- reports/
|-- docs/
|   |-- api.md
|   \-- schema.md
|
|-- instance/
|-- .env.example
|-- .gitignore
|-- .dockerignore
|-- Dockerfile
|-- docker-compose.yml
|-- docker-compose.dev.yml
|-- Makefile
|-- requirements.txt
|-- setup.cfg
|-- run.py
|-- CONTRIBUTING.md
\-- README.md
```

## Установка

Клонировать репозиторий:

```bash
git clone https://github.com/Hudaynazar250406/diary.git
cd diary
```

Создать виртуальное окружение:

```bash
python -m venv venv
```

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

Если PowerShell блокирует выполнение скриптов, один раз выполните:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Git Bash / Linux / macOS

```bash
source venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

## Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```powershell
Copy-Item .env.example .env
```

```bash
cp .env.example .env
```

Пример конфигурации:

```env
DATABASE_URL=postgresql+psycopg://studenttrack:studenttrack@localhost:5432/studenttrack
SECRET_KEY=replace-with-a-long-random-secret
APP_PORT=5000
FLASK_ENV=development

# Переменные для docker compose (подставляются в docker-compose.yml)
POSTGRES_USER=studenttrack
POSTGRES_PASSWORD=studenttrack
POSTGRES_DB=studenttrack
```

Файл `.env` содержит локальную конфигурацию и не должен добавляться в Git. Настройки в контейнеры передаются только через переменные окружения — секреты в образ не помещаются (`.env` исключён в `.dockerignore`).

## Запуск в Docker (основной способ)

### Архитектура окружения

```text
                хост
                  |
               :8080 (единственный опубликованный порт, сеть frontend)
                  |
        [ nginx:1.27-alpine ]      <- балансировщик, retry на другой экземпляр
            |           |
   [ web x2 (gunicorn, USER app) ] <- replicas: 2, порты наружу не открыты
                  |
      [ postgres:16-alpine ]       <- порт БД не публикуется, данные в volume
                  |
       сеть backend (internal, без доступа наружу)
```

Эксплуатационные требования зафиксированы в `CONTRIBUTING.md`: нет тегов `latest`, приложение не от root, секреты только через переменные окружения, healthcheck у каждого сервиса, лишние порты не публикуются. Часть требований проверяется автоматически (см. `make container-check`).

### Быстрый старт

```bash
cp .env.example .env        # задать SECRET_KEY
docker compose up --build   # сборка и запуск всего окружения
make migrate                # миграции БД внутри контейнера
```

Приложение доступно через Nginx: http://localhost:8080

| Порт | Назначение |
|---|---|
| `8080` | Nginx — единственный опубликованный порт (HTTP) |
| `5000` | Gunicorn внутри сети `backend` — с хоста недоступен |
| `5432` | PostgreSQL внутри сети `backend` — на хост не публикуется |

### Автоматическая проверка окружения

```bash
make container-check
```

Скрипт `scripts/container_check.py` проверяет:

- конфигурацию: отсутствие тегов `latest`, неопубликованность порта БД и порта приложения, наличие healthcheck у всех сервисов, внутреннюю сеть backend, непривилегированного пользователя в Dockerfile, минимум два экземпляра web;
- сборку образа и запуск окружения (ожидание `healthy` у всех контейнеров);
- доступность сервиса через Nginx;
- балансировку: не менее двух разных идентификаторов `instance` в ответах `/health`;
- пользователя процесса web (не `root`);
- отказоустойчивость: остановку одного экземпляра, доступность сервиса, корректное завершение контейнера по SIGTERM (код выхода 0) и восстановление экземпляра.

Изменение контейнерного окружения принимается только при успешном выполнении этой команды.

### Масштабирование и отказоустойчивость

- Запущено два экземпляра приложения (`deploy.replicas: 2`). Встроенный DNS Docker отдаёт для имени `web` адреса обеих реплик; Nginx (`resolver 127.0.0.11 valid=5s`) периодически перечитывает список и распределяет запросы между экземплярами.
- Ответ `/health` содержит `instance` — hostname контейнера, обработавшего запрос. Это позволяет увидеть балансировку на практике.
- При недоступности одного экземпляра Nginx повторяет идемпотентный запрос на другом (`proxy_next_upstream error timeout http_502 http_503`). POST-запросы не дублируются.
- Проверка вручную: `docker compose stop` одного контейнера web (например, `docker stop studenttrack-web-2`) — сервис продолжает отвечать через http://localhost:8080/health.

Что ограничивает горизонтальное масштабирование приложения сейчас:

- **PostgreSQL — единственный компонент с состоянием.** Реплики web читают и пишут в один primary-экземпляр; для масштабирования самой БД потребовалось бы внешнее решение (managed PostgreSQL, Patroni и т. п.). До этого предела сами реплики web масштабируются свободно.
- **Миграции БД должны выполняться один раз** (`make migrate`), а не при старте каждой реплики, иначе возможна гонка между конкурирующими миграциями.
- **Сессии — клиентские подписанные cookie Flask**, состояние на сервере не хранится, поэтому реплики взаимозаменяемы и sticky-сессии не нужны. Обязательное требование: одинаковый `SECRET_KEY` у всех экземпляров (задаётся через `.env`).
- Общих файлов (загрузок) у приложения нет; при их появлении потребуется общее хранилище (общий volume или объектное хранилище).
- Ограничения Nginx open source: нет активных проверок upstream, список реплик обновляется по DNS (`valid=5s`), а не мгновенно.

### Сохранность данных, бэкап и восстановление

Данные PostgreSQL хранятся в именованном volume `studenttrack_pgdata` и переживают пересоздание контейнеров и обновление образа:

```bash
# проверка сохранности после пересоздания
docker compose down
docker compose up -d
# данные на месте
```

Резервное копирование и восстановление выполняются в контейнерной среде:

```bash
make backup     # pg_dump в backups/backup_YYYYMMDD_HHMMSS.sql
make restore    # восстановление из последнего дампа (или: python scripts/restore.py backups/<файл>.sql)
```

Восстановление в новый (пустой) volume — полный сценарий:

```bash
docker compose down -v    # удалить контейнеры И volume (данные стёрты)
docker compose up -d
make restore              # данные восстановлены из дампа
```

### Остановка окружения

```bash
docker compose down
```

Приложение завершается корректно: Docker посылает SIGTERM, Gunicorn прекращает приём новых соединений и дожидается завершения текущих запросов (`stop_grace_period: 30s`).

## База данных (локальная разработка без полного контура)

Проект использует **PostgreSQL 16+** в качестве основной СУБД.

SQLite не используется для запуска приложения: при конкурентной записи нескольких пользователей одновременно (администратор, преподаватели, студенты) SQLite допускает только одну активную пишущую транзакцию и блокирует базу целиком, что приводит к ошибкам `database is locked`. PostgreSQL использует MVCC и построчные блокировки, обеспечивая корректную параллельную запись. Исключение — автоматические тесты, которые продолжают использовать изолированную временную SQLite-базу для быстрого прогона (см. раздел «Тестирование»).

### Вариант 1. БД в Docker, приложение локально

В основном `docker-compose.yml` порт БД не публикуется. Для локальной разработки используется оверрейд `docker-compose.dev.yml`, который открывает порт 5432 на хост:

```bash
make dev-db
python run.py
```

### Вариант 2. Локальная установка PostgreSQL

Установите PostgreSQL 16 (например, через `winget install --id=PostgreSQL.PostgreSQL.16 -e` на Windows) и создайте базу данных и пользователя:

```sql
CREATE USER studenttrack WITH PASSWORD 'studenttrack';
CREATE DATABASE studenttrack OWNER studenttrack;
```

## Запуск приложения локально

Перед первым запуском примените миграции — они создают все таблицы в базе:

```bash
python -m flask --app run db upgrade
```

(в контейнерном окружении та же операция — `make migrate`).

Запуск:

```bash
python run.py
```

После запуска приложение доступно по адресу:

```text
http://127.0.0.1:5000
```

### Создание администратора

Для доступа к панели администратора создайте учётную запись через CLI-команду:

```bash
flask --app run create-admin <username> <email>
```

Команда запросит пароль (минимум 8 символов). Роль `admin` можно назначить только через CLI — это ограничение реализовано намеренно, назначить её через веб-API нельзя.

Изменить роль существующего пользователя (`student` или `teacher`):

```bash
flask --app run set-role <username> <role>
```

## Проверка работоспособности

```text
GET /health
```

```bash
curl http://localhost:8080/health    # контейнерное окружение (через Nginx)
curl http://127.0.0.1:5000/health    # локальный запуск
```

Ожидаемый ответ (`instance` — hostname контейнера, обработавшего запрос):

```json
{
  "status": "ok",
  "instance": "3f2a1b9c7d"
}
```

## Роли и разграничение доступа

| Роль | Права доступа |
|---|---|
| `student` | Доступ только к собственным данным через `/me/*` (свои дисциплины, расписание, оценки). |
| `teacher` | Просмотр групп, студентов, дисциплин, учебных планов; создание/изменение/удаление оценок и расписания. |
| `admin` | Полный доступ ко всем сущностям; управление пользователями (роли, привязка студента). Назначается только через CLI. |

Доступ на уровне маршрутов контролируется декораторами `login_required` и `role_required` (`app/permissions.py`).

## Веб-интерфейс

- `GET /register`, `POST /register` — регистрация (новый пользователь получает роль `student`);
- `GET /login`, `POST /login` — вход по username или email;
- `POST /logout` — выход;
- `GET /dashboard` — панель управления с разделами в зависимости от роли: обзор, группы, студенты, дисциплины, учебные планы, расписание, оценки, пользователи (для `admin`), либо личные разделы для `student` (мои дисциплины / моё расписание / мои оценки).

Веб-интерфейс обращается к тому же HTTP API через JavaScript `fetch()` — отдельного front-end сервера не требуется.

## API

### Health-check

| Метод | URL | Описание |
|---|---|---|
| GET | `/health` | Проверка работоспособности приложения; в ответе поле `instance` — идентификатор экземпляра |

### Аутентификация

| Метод | URL | Описание |
|---|---|---|
| GET/POST | `/register` | Регистрация пользователя |
| GET/POST | `/login` | Вход по username или email |
| POST | `/logout` | Выход из системы |

### Учебные группы

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/groups` | Список групп | teacher, admin |
| GET | `/groups/<id>` | Группа по ID | teacher, admin |
| POST | `/groups` | Создать группу | admin |
| PUT | `/groups/<id>` | Изменить группу | admin |
| DELETE | `/groups/<id>` | Удалить группу | admin |

### Студенты

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/students` | Список студентов (фильтр по `group_id`) | teacher, admin |
| GET | `/students/<id>` | Студент по ID | teacher, admin |
| POST | `/students` | Создать студента | admin |
| PUT | `/students/<id>` | Изменить студента | admin |
| DELETE | `/students/<id>` | Удалить студента | admin |

### Дисциплины

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/disciplines` | Список дисциплин | teacher, admin |
| GET | `/disciplines/<id>` | Дисциплина по ID | teacher, admin |
| POST | `/disciplines` | Создать дисциплину | admin |
| PUT | `/disciplines/<id>` | Изменить дисциплину | admin |
| DELETE | `/disciplines/<id>` | Удалить дисциплину | admin |

### Учебные планы

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/study_plans` | Список учебных планов | teacher, admin |
| GET | `/study_plans/<id>` | Учебный план по ID | teacher, admin |
| POST | `/study_plans` | Создать учебный план | admin |
| PUT | `/study_plans/<id>` | Изменить учебный план | admin |
| DELETE | `/study_plans/<id>` | Удалить учебный план | admin |

### Оценки

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/grades` | Список оценок | teacher, admin |
| GET | `/grades/<id>` | Оценка по ID | teacher, admin |
| POST | `/grades` | Создать оценку | teacher, admin |
| PUT | `/grades/<id>` | Изменить оценку | teacher, admin |
| DELETE | `/grades/<id>` | Удалить оценку | teacher, admin |

### Расписание

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/schedules` | Список занятий | teacher, admin |
| POST | `/schedules` | Создать занятие | teacher, admin |
| PUT | `/schedules/<id>` | Изменить занятие | teacher, admin |
| DELETE | `/schedules/<id>` | Удалить занятие | teacher, admin |

### Личный кабинет студента

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/me/disciplines` | Мои дисциплины | student |
| GET | `/me/schedule` | Моё расписание | student |
| GET | `/me/grades` | Мои оценки | student |

### Администрирование пользователей

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| GET | `/admin/users` | Список пользователей | admin |
| PUT | `/admin/users/<id>/role` | Назначить роль student/teacher | admin |
| PUT | `/admin/users/<id>/student` | Привязать/отвязать студента | admin |

## Основные сущности

```text
Group
Student
Discipline
StudyPlan
Grade
Schedule
User
```

Основные связи:

```text
Group        1:N  Student
Group        1:N  StudyPlan
Group        1:N  Schedule
Discipline   1:N  StudyPlan
Discipline   1:N  Grade
Discipline   1:N  Schedule
Student      1:N  Grade
Student      1:1  User (через users.student_id)
```

Связи внешних ключей:

```text
groups.id       -> students.group_id
groups.id       -> study_plans.group_id
groups.id       -> schedules.group_id
disciplines.id  -> study_plans.discipline_id
disciplines.id  -> grades.discipline_id
disciplines.id  -> schedules.discipline_id
students.id     -> grades.student_id
students.id     -> users.student_id (unique)
```

Ограничения целостности на уровне БД:

- `grades.grade` — CHECK, диапазон 1–5;
- `schedules.weekday` — CHECK, диапазон 1–7 (1 — понедельник, 7 — воскресенье);
- `users.username`, `users.email` — UNIQUE;
- `users.student_id` — UNIQUE (один аккаунт на одного студента).

Подробное описание структуры базы данных: `docs/schema.md`.

## Бизнес-правила

### Оценки

- значение оценки — только целое число от 1 до 5;
- оценку можно выставить только по дисциплине, входящей в учебный план группы студента;
- при нарушении правил сервер возвращает `400 Bad Request`, при отсутствии студента/дисциплины — `404 Not Found`.

### Расписание

- группа и дисциплина, указанные в занятии, должны существовать;
- дисциплина должна присутствовать в учебном плане указанной группы;
- день недели — целое число от 1 до 7;
- время окончания должно быть позже времени начала;
- у одной группы не может быть двух занятий, пересекающихся по времени в один день недели.

### Регистрация и роли

- новый пользователь всегда получает роль `student`;
- username и email должны быть уникальны;
- пароль — минимум 8 символов, хранится только в виде хеша;
- роль `admin` невозможно получить через веб-интерфейс или API — только через CLI-команды `create-admin` / `set-role`.

## Обработка ошибок

Единый формат ошибок: `{"error": "текст ошибки"}`.

| Ситуация | HTTP-код |
|---|---|
| Успешное получение данных | `200 OK` |
| Успешное создание записи | `201 Created` |
| Успешное удаление | `204 No Content` |
| Некорректный запрос / нарушение бизнес-правила | `400 Bad Request` |
| Недостаточно прав | `403 Forbidden` |
| Ресурс не найден | `404 Not Found` |
| Внутренняя ошибка сервера | `500 Internal Server Error` |

## Тестирование

Автоматические тесты используют изолированную временную SQLite-базу (создаётся и уничтожается на каждый тестовый прогон) — это сознательное решение, не связанное с отказом от PostgreSQL в целом: тесты не требуют внешнего сервера БД и работают быстрее, при этом полностью покрывают бизнес-логику, так как код работает с БД только через SQLAlchemy ORM.

Запуск всех тестов:

```bash
python -m pytest -v
```

Запуск тестов конкретного модуля:

```bash
python -m pytest tests/test_schedules.py -v
```

Тестовые модули:

| Файл | Покрываемая функциональность |
|---|---|
| `test_health.py` | health-check и идентификатор экземпляра |
| `test_groups.py` | CRUD групп |
| `test_students.py` | CRUD студентов |
| `test_disciplines.py` | CRUD дисциплин |
| `test_study_plans.py` | CRUD учебных планов |
| `test_grades.py` | CRUD оценок и бизнес-правила |
| `test_schedules.py` | CRUD расписания, пересечения занятий |
| `test_auth.py` | регистрация и авторизация |
| `test_permissions.py` | декораторы доступа по ролям |
| `test_admin.py` | администрирование пользователей |
| `test_commands.py` | CLI-команды create-admin, set-role |
| `test_me.py` | личный кабинет студента |

## Статический анализ

```bash
flake8 .
```

Если команда завершается без вывода — проверка пройдена успешно.

## Git-процесс

Разработка ведётся через отдельные feature-ветки с последующим Pull Request в `main`:

```text
Issue -> Feature branch -> Commits -> Pull Request -> Code Review -> Merge into main
```

Примеры веток:

```text
feature/flask-sqlite-init
feature/disciplines
feature/study-plans
feature/crud-grades
feature/groups-students-crud
feature/front-ui
feature/postgres-migration
```

Перед объединением ветки необходимо убедиться, что проходят тесты и статический анализ:

```bash
python -m pytest -v
flake8 .
```

Для изменений контейнерного окружения дополнительно обязательна команда `make container-check`.

## Документация

- `docs/schema.md` — структура базы данных, таблицы, внешние ключи, бизнес-правила;
- `docs/api.md` — описание HTTP API.

## Статус проекта

Реализовано и объединено в `main`:

- HTTP API и веб-интерфейс (dashboard) с ролевой моделью;
- регистрация, авторизация, управление пользователями;
- CRUD для групп, студентов, дисциплин, учебных планов, оценок, расписания;
- обработка ошибок, health-check;
- основная СУБД — PostgreSQL 16, миграции схемы через Alembic/Flask-Migrate;
- контейнерное окружение: Nginx-балансировщик, два экземпляра приложения (Gunicorn, непривилегированный пользователь), PostgreSQL в изолированной сети с volume, ограничения ресурсов, healthcheck'и;
- автоматическая проверка окружения (`make container-check`);
- скрипты резервного копирования и восстановления базы данных (`scripts/backup.py`, `scripts/restore.py`);
- автоматические тесты (103) и статический анализ кода.
