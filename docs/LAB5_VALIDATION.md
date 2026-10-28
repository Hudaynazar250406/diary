# Реально выполненные проверки ЛР5

Дата задания: 29 октября 2026. Среда проверки: Linux, Python 3.12.8. CI настроен на Python 3.13. Это локальная проверка в песочнице, не результат GitLab pipeline.

- `make quality`: успешно, исходные исключения Flake8 не расширены.
- `make config-guard`: успешно относительно исходной main.
- `make verify PYTEST_WORKERS=0`: тесты и coverage — 155 passed на SQLite, health HTTP 200.
- Coverage приложения: 93.40%, обязательный минимум 80% сохранён.
- `make security-deps`: известных уязвимостей не найдено на момент аудита. Обновлены Flask, python-dotenv и pytest по результатам pip-audit.
- Девять регрессионных тестов guard входят в общий прогон. Baseline — 153 определения функций; параметризация pytest даёт 155 случаев. Дополнительно включены шесть тестов безопасного создания .env.
- YAML прочитан парсером, порядок восьми стадий и обязательные needs проверены guard.

Не проверено: Docker Engine/Compose/Buildx, PostgreSQL server, Gitleaks и Trivy отсутствуют в песочнице. Поэтому PostgreSQL-тесты, миграции, backup/restore, container-check, сборка/сканирование образа и registry push не объявляются успешными. GitLab CI Lint и настройки runners/approvals нужно выполнить в реальном GitLab.

GitHub хранит новую ветку, но не исполняет .gitlab-ci.yml как GitHub Actions. Удалённая main не изменяется.

Повторная проверка 29 октября 2026: `make quality`, `make config-guard`, `make verify PYTEST_WORKERS=0`, `make security-deps` — успешно. Существующий .env не изменялся, удалённая main не изменяется. Локальная .env не создавалась в копии репозитория и в коммит не включается.
