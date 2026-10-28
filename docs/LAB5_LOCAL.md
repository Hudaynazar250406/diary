# ЛР5: быстрый локальный запуск

Полная настройка GitLab и сценарии защиты находятся в [LAB5_CI.md](LAB5_CI.md). CI остаётся GitLab CI/CD по условию задания; GitHub хранит ветку исходников.

## Забрать ветку

В существующем локальном репозитории (сначала проверьте `git status`, не удаляйте незакоммиченные изменения):

```bash
git fetch origin
git switch lab5/continuous-integration
git pull --ff-only origin lab5/continuous-integration
```

Если репозиторий ещё не клонирован:

```bash
git clone --branch lab5/continuous-integration https://github.com/Hudaynazar250406/diary.git
cd diary
```

## Проверки без Docker

Нужен Python 3.11+ (CI использует 3.13), Git и make. На Windows рекомендуется WSL.

```bash
python -m venv .venv
source .venv/bin/activate
make setup
make config-guard
make verify PYTEST_WORKERS=0
make security-deps
```

Без `TEST_DATABASE_URL` используется временная SQLite. Результаты фактической проверки: [LAB5_VALIDATION.md](LAB5_VALIDATION.md).

## Контейнеры

Нужны Docker Engine или Docker Desktop с Compose v2.

Если `.env` отсутствует, выполните:

```bash
make env-init
```

Команда генерирует случайные секреты, не печатает их и никогда не перезаписывает существующий `.env`. Не задавайте новые пароли для существующего PostgreSQL volume: используйте действительные настройки окружения. `.env` не коммитьте.

```bash
make up
make migrate
make container-check
```

Открыть приложение: http://127.0.0.1:8080. Если 8080 занят, сначала остановите конфликтующий процесс. `container-check` запускает и проверяет Compose-стек; не запускайте его против production.

Обычная остановка без удаления данных:

```bash
make down
```

Не используйте `docker compose down -v` для существующей рабочей БД.

## Что ещё нужно настроить

GitLab-проект, runners `lab5-python` и `lab5-docker`, обязательные approvals и protected main настраиваются по полной инструкции. GitHub push не запускает `.gitlab-ci.yml`. В GitLab необходимо выполнить CI Lint и реальный pipeline; результат Docker/PostgreSQL-проверок пока не объявляется успешным.
