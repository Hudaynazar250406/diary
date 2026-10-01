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
- health-check приложения;
- хранение данных в PostgreSQL;
- контейнеризация через Docker и Docker Compose;
- автоматические тесты (pytest) и статический анализ кода (flake8).

## Технологии

- Python 3.13
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- PostgreSQL 16 (psycopg2-binary)
- Werkzeug (хеширование паролей)
- Marshmallow (валидация)
- python-dotenv
- Jinja2, HTML/CSS, JavaScript (fetch API)
- Docker, Docker Compose
- pytest, pytest-cov, flake8
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
|   |-- schemas/
|   |-- services/
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
|-- tests/
|   |-- conftest.py
|   |-- test_health.py
|   |-- test_groups.py
|   |-- test_students.py
|   |-- test_disciplines.py
|   |-- test_study_plans.py
|   |-- test_grades.py
|   |-- test_schedules.py
|   |-- test_auth.py
|   |-- test_permissions.py
|   |-- test_admin.py
|   |-- test_commands.py
|   \-- test_me.py
|
|-- docs/
|   |-- api.md
|   \-- schema.md
|
|-- instance/
|-- .env.example
|-- .gitignore
|-- Dockerfile
|-- docker-compose.yml
|-- Makefile
|-- requirements.txt
|-- run.py
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

## База данных

Проект использует **PostgreSQL 16** в качестве основной СУБД.

SQLite не используется для запуска приложения: при конкурентной записи нескольких пользователей одновременно (администратор, преподаватели, студенты) SQLite допускает только одну активную пишущую транзакцию и блокирует базу целиком, что приводит к ошибкам `database is locked`. PostgreSQL использует MVCC и построчные блокировки, обеспечивая корректную параллельную запись. Исключение — автоматические тесты, которые продолжают использовать изолированную временную SQLite-базу для быстрого прогона (см. раздел «Тестирование»).

### Вариант 1. Через Docker (рекомендуется)

```bash
docker compose up -d db
```

Подничт контейнер PostgreSQL 16 с базой `studenttrack`, пользователем `studenttrack` и паролем `studenttrack` на порте 5432.

Полный запуск приложения и базы данных одной командой:

```bash
docker compose up --build
```

Приложение будет доступно на http://localhost:5000.

### Вариант 2. Локальная установка PostgreSQL

Установите PostgreSQL 16 (например, через `winget install --id=PostgreSQL.PostgreSQL.16 -e` на Windows) и создайте базу данных и пользователя:

```sql
CREATE USER studenttrack WITH PASSWORD 'studenttrack';
CREATE DATABASE studenttrack OWNER studenttrack;
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
DATABASE_URL=postgresql://studenttrack:studenttrack@localhost:5432/studenttrack
SECRET_KEY=replace-with-a-long-random-secret
APP_PORT=5000
FLASK_ENV=development
```

Файл `.env` содержит локальную конфигурацию и не должен добавляться в Git.

## Запуск приложения

При первом запуске таблицы создаются автоматически (`db.create_all()` внутри `create_app`).

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
curl http://127.0.0.1:5000/health
```

Ожидаемый ответ:

```json
{
  "status": "ok"
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
| GET | `/health` | Проверка работоспособности приложения |

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

Подробное обисание структуры базы данных: `docs/schema.md`.

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
| `test_health.py` | health-check |
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

## Документация

- `docs/schema.md` — структура базы данных, таблицы, внешние ключи, бизнес-правила;
- `docs/api.md` — описание HTTP API.

## Статус проекта

Реализовано и объединено в `main`:

- HTTP API и веб-интерфейс (dashboard) с ролевой моделью;
- регистрация, авторизация, управление пользователями;
- CRUD для групп, студентов, дисциплин, учебных планов, оценок, расписания;
- обработка ошибок, health-check;
- автоматические тесты (102) и статический анализ кода.

В процессе рассмотрения (Pull Request):

- переход основной СУБД с SQLite на PostgreSQL 16;
- контейнеризация приложения и базы данных через Docker Compose.
