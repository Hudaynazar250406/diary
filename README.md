# StudentTrack

StudentTrack - учебное Flask-приложение для учета успеваемости студентов.

Система предназначена для хранения информации о студентах, учебных группах, дисциплинах, учебных планах и оценках.

## Возможности

На текущем этапе реализуются:

- работа с учебными группами;
- работа со студентами;
- управление дисциплинами;
- управление учебными планами;
- управление оценками;
- проверка принадлежности дисциплины учебному плану группы;
- проверка диапазона оценок;
- HTTP API;
- обработка ошибок;
- health-check приложения;
- хранение данных в SQLite;
- автоматические тесты;
- статический анализ кода с помощью Flake8.

## Технологии

Проект использует:

- Python
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- SQLite
- python-dotenv
- pytest
- Flake8
- Git
- GitHub

## Структура проекта

```text
studenttrack/
|-- app/
|   |-- __init__.py
|   |-- config.py
|   |-- errors.py
|   |-- extensions.py
|   |
|   |-- models/
|   |   |-- __init__.py
|   |   |-- group.py
|   |   |-- student.py
|   |   |-- discipline.py
|   |   |-- study_plan.py
|   |   \-- grade.py
|   |
|   |-- routes/
|   |   |-- __init__.py
|   |   |-- health.py
|   |   |-- groups.py
|   |   |-- students.py
|   |   |-- disciplines.py
|   |   |-- study_plans.py
|   |   \-- grades.py
|   |
|   |-- schemas/
|   \-- services/
|
|-- tests/
|   |-- conftest.py
|   |-- test_health.py
|   |-- test_groups.py
|   |-- test_students.py
|   |-- test_disciplines.py
|   |-- test_study_plans.py
|   \-- test_grades.py
|
|-- docs/
|   |-- api.md
|   \-- schema.md
|
|-- instance/
|-- .env.example
|-- .gitignore
|-- .flake8
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
python -m venv .venv
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Git Bash

```bash
source .venv/Scripts/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

## Переменные окружения

Создайте файл `.env` на основе `.env.example`.

Для PowerShell:

```powershell
Copy-Item .env.example .env
```

Для Git Bash:

```bash
cp .env.example .env
```

Пример конфигурации:

```env
DATABASE_URL=sqlite:///studenttrack.db
```

Файл `.env` содержит локальную конфигурацию и не должен добавляться в Git.

## Запуск приложения

Запустить приложение можно командой:

```bash
python run.py
```

После запуска API будет доступно по адресу:

```text
http://127.0.0.1:5000
```

## Проверка работоспособности

Для проверки состояния приложения используется endpoint:

```text
GET /health
```

Пример запроса:

```bash
curl http://127.0.0.1:5000/health
```

Ожидаемый ответ:

```json
{
  "status": "ok"
}
```

HTTP-код ответа:

```text
200 OK
```

## API

### Health-check

| Метод | URL | Описание |
|---|---|---|
| GET | `/health` | Проверка работоспособности приложения |

### Учебные группы

| Метод | URL | Описание |
|---|---|---|
| GET | `/groups` | Получить список групп |
| GET | `/groups/<id>` | Получить группу по ID |
| POST | `/groups` | Создать группу |
| PUT | `/groups/<id>` | Изменить группу |
| DELETE | `/groups/<id>` | Удалить группу |

### Студенты

| Метод | URL | Описание |
|---|---|---|
| GET | `/students` | Получить список студентов |
| GET | `/students/<id>` | Получить студента по ID |
| POST | `/students` | Создать студента |
| PUT | `/students/<id>` | Изменить студента |
| DELETE | `/students/<id>` | Удалить студента |

### Дисциплины

| Метод | URL | Описание |
|---|---|---|
| GET | `/disciplines` | Получить список дисциплин |
| GET | `/disciplines/<id>` | Получить дисциплину по ID |
| POST | `/disciplines` | Создать дисциплину |
| PUT | `/disciplines/<id>` | Изменить дисциплину |
| DELETE | `/disciplines/<id>` | Удалить дисциплину |

### Учебные планы

| Метод | URL | Описание |
|---|---|---|
| GET | `/study_plans` | Получить список учебных планов |
| GET | `/study_plans/<id>` | Получить учебный план по ID |
| POST | `/study_plans` | Создать учебный план |
| PUT | `/study_plans/<id>` | Изменить учебный план |
| DELETE | `/study_plans/<id>` | Удалить учебный план |

### Оценки

| Метод | URL | Описание |
|---|---|---|
| GET | `/grades` | Получить список оценок |
| GET | `/grades/<id>` | Получить оценку по ID |
| POST | `/grades` | Создать оценку |
| PUT | `/grades/<id>` | Изменить оценку |
| DELETE | `/grades/<id>` | Удалить оценку |

## Основные сущности

В проекте используются следующие основные сущности:

```text
Group
Student
Discipline
StudyPlan
Grade
```

Основные связи:

```text
Group 1:N Student

Group 1:N StudyPlan

Discipline 1:N StudyPlan

Student 1:N Grade

Discipline 1:N Grade
```

Связи внешних ключей:

```text
groups.id -> students.group_id

groups.id -> study_plans.group_id

disciplines.id -> study_plans.discipline_id

students.id -> grades.student_id

disciplines.id -> grades.discipline_id
```

Более подробное описание структуры базы данных находится в:

```text
docs/schema.md
```

## Работа с оценками

Для создания оценки необходимо передать:

```json
{
  "student_id": 1,
  "discipline_id": 1,
  "grade": 5
}
```

Пример запроса:

```bash
curl -X POST http://127.0.0.1:5000/grades \
  -H "Content-Type: application/json" \
  -d '{"student_id":1,"discipline_id":1,"grade":5}'
```

При успешном создании возвращается:

```text
201 Created
```

Пример ответа:

```json
{
  "id": 1,
  "student_id": 1,
  "discipline_id": 1,
  "grade": 5,
  "date": "2026-09-10"
}
```

Получение всех оценок:

```bash
curl http://127.0.0.1:5000/grades
```

Получение оценки по ID:

```bash
curl http://127.0.0.1:5000/grades/1
```

Изменение оценки:

```bash
curl -X PUT http://127.0.0.1:5000/grades/1 \
  -H "Content-Type: application/json" \
  -d '{"grade":4}'
```

Удаление оценки:

```bash
curl -X DELETE http://127.0.0.1:5000/grades/1
```

## Бизнес-правила

### Диапазон оценки

Оценка может принимать только значения:

```text
1
2
3
4
5
```

Условие:

```text
1 <= grade <= 5
```

Если передано другое значение, сервер возвращает:

```text
400 Bad Request
```

Например:

```json
{
  "student_id": 1,
  "discipline_id": 1,
  "grade": 6
}
```

является некорректным запросом.

### Проверка учебного плана

Оценка может быть выставлена студенту только по дисциплине, которая присутствует в учебном плане его группы.

Порядок проверки:

```text
student_id
    |
    v
Student
    |
    v
group_id

group_id + discipline_id
          |
          v
      StudyPlan
          |
          v
     запись есть?
       /      \
      да      нет
      |        |
      v        v
   Grade    HTTP 400
```

Перед созданием оценки приложение:

1. Получает студента по `student_id`.
2. Проверяет существование студента.
3. Получает группу студента.
4. Проверяет существование дисциплины.
5. Ищет запись `StudyPlan` по группе и дисциплине.
6. Если запись отсутствует, создание оценки запрещается.
7. Если запись существует, оценка сохраняется в базе данных.

Условие проверки:

```text
StudyPlan.group_id = Student.group_id

AND

StudyPlan.discipline_id = requested_discipline_id
```

Если студент не существует:

```text
404 Not Found
```

Если дисциплина не существует:

```text
404 Not Found
```

Если дисциплина отсутствует в учебном плане:

```text
400 Bad Request
```

## Обработка ошибок

API использует стандартные HTTP-коды.

| Ситуация | HTTP-код |
|---|---|
| Успешное получение данных | `200 OK` |
| Успешное создание записи | `201 Created` |
| Некорректный запрос | `400 Bad Request` |
| Некорректная оценка | `400 Bad Request` |
| Дисциплина отсутствует в StudyPlan | `400 Bad Request` |
| Ресурс не найден | `404 Not Found` |
| Внутренняя ошибка сервера | `500 Internal Server Error` |

## Тестирование

Для запуска всех автоматических тестов:

```bash
python -m pytest -v
```

Для запуска тестов конкретного модуля:

```bash
python -m pytest tests/test_grades.py -v
```

Тесты оценок проверяют:

- создание оценки со значением 1;
- создание оценки со значением 5;
- запрет оценки 0;
- запрет оценки 6;
- попытку создания оценки для несуществующего студента;
- попытку создания оценки для несуществующей дисциплины;
- запрет оценки по дисциплине, отсутствующей в StudyPlan;
- получение оценок;
- получение оценки по ID;
- изменение оценки;
- удаление оценки.

## Статический анализ

Для проверки качества и оформления Python-кода используется Flake8.

Запуск:

```bash
flake8 .
```

Если команда завершается без вывода ошибок, статический анализ успешно пройден.

Конфигурация Flake8 исключает из проверки служебные директории, например:

```text
.venv
venv
__pycache__
.pytest_cache
instance
```

## База данных

На текущем этапе проекта используется SQLite.

Пример строки подключения:

```text
sqlite:///studenttrack.db
```

SQLite используется для первой лабораторной работы и позволяет запускать проект без отдельного сервера базы данных.

Работа с базой выполняется через SQLAlchemy.

Файл базы данных не должен добавляться в Git.

В дальнейших этапах проекта предусматривается переход на PostgreSQL.

## Git-процесс

Разработка выполняется через отдельные feature-ветки.

Общий процесс:

```text
Issue
  |
  v
Feature branch
  |
  v
Commits
  |
  v
Pull Request
  |
  v
Code Review
  |
  v
Merge into main
```

Примеры веток:

```text
feature/flask-sqlite-init
feature/disciplines
feature/study-plans
feature/crud-grades
```

Для каждой задачи создается отдельная ветка.

Изменения не должны отправляться непосредственно в `main`.

После завершения задачи создается Pull Request.

Перед объединением ветки необходимо проверить:

```bash
python -m pytest -v
flake8 .
```

## Переменные и локальные файлы

В Git не должны попадать:

```text
.env
.venv/
venv/
__pycache__/
.pytest_cache/
instance/*.db
instance/*.sqlite
instance/*.sqlite3
```

Пример конфигурации для разработчика хранится в:

```text
.env.example
```

## Документация

Дополнительная документация находится в каталоге:

```text
docs/
```

Файл:

```text
docs/schema.md
```

содержит описание структуры базы данных, таблиц, внешних ключей и бизнес-правил.

Файл:

```text
docs/api.md
```

предназначен для более подробного описания HTTP API.

## Статус проекта

Проект находится в разработке.

На текущем этапе основной задачей является создание минимально работоспособного Flask-приложения, которое включает:

- HTTP API;
- реляционную базу данных;
- связанные сущности;
- CRUD-операции;
- бизнес-правила;
- обработку ошибок;
- автоматические тесты;
- статический анализ;
- командный Git-процесс.

Следующие этапы проекта могут включать:

- PostgreSQL;
- миграции базы данных;
- Docker;
- авторизацию;
- разграничение ролей;
- резервное копирование;
- формирование отчетов.