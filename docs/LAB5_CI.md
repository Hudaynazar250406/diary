# ЛР5 — Continuous Integration

## Назначение и допущения

CI выбран GitLab: одна система для исходников, pipelines, artifacts и registry. В отличие от отдельного Jenkins/TeamCity не требуется связывать дополнительные сервисы. Прикладные проверки выполняются через Makefile. JUnit и Cobertura интегрированы в pipeline, SARIF сохраняется скачиваемым файлом (не выдаётся за GitLab SAST). Защита состоит из guard, Code Owners, approvals и запрета прямого push. Обязательные Code Owner approvals зависят от редакции/лицензии GitLab.

# ДОПУЩЕНИЕ: GitHub хранит исходники, а CI выполняется в GitLab после добавления GitLab remote.
# ДОПУЩЕНИЕ: PostgreSQL 16 существующего Compose/volume сохранён; отдельная БД CI — PostgreSQL 15 по заданию.
# ДОПУЩЕНИЕ: username GitLab владельца совпадает с Hudaynazar250406; проверьте CODEOWNERS и добавьте независимого второго участника. Автор MR не должен одобрять себя.

## Начать локально без Docker

```bash
git fetch origin
git switch lab5/continuous-integration
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell вместо предыдущей команды:
# .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
make setup
make config-guard
make verify PYTEST_WORKERS=0
make security-deps
```

Нужен Python 3.11+ (CI использует 3.13), Git, make. На Windows make можно установить через MSYS2 либо выполнять команды в WSL. Без TEST_DATABASE_URL тесты используют одноразовую SQLite; локальное приложение без DATABASE_URL — SQLite в instance/. В Compose приложение использует PostgreSQL. Make setup устанавливает прикладные и CI-зависимости.

## Локальные контейнеры

Не заменяйте пароль существующего PostgreSQL volume случайным новым: в .env должны остаться действующие настройки. Для первого чистого запуска:

```bash
cp .env.example .env
python - <<'PY'
from pathlib import Path
import secrets
p = Path('.env')
s = p.read_text()
if 'POSTGRES_PASSWORD=\n' not in s or 'SECRET_KEY=\n' not in s:
    raise SystemExit('Файл уже заполнен: проверьте вручную, не перезаписывайте секреты')
s = s.replace('POSTGRES_PASSWORD=\n', f'POSTGRES_PASSWORD={secrets.token_hex(24)}\n')
s = s.replace('SECRET_KEY=\n', f'SECRET_KEY={secrets.token_hex(32)}\n')
p.write_text(s)
p.chmod(0o600)
PY
make up
make migrate
make container-check
```

Приложение: http://127.0.0.1:8080. Не коммитьте .env. Пустые POSTGRES_PASSWORD/SECRET_KEY намеренно запрещены в Compose. Не запускайте `docker compose down -v` для существующей рабочей БД. Прежде чем копировать .env.example, убедитесь, что собственного .env ещё нет; команда cp перезаписывает файл.

## Тесты на PostgreSQL

Для одноразовой отдельной БД задайте TEST_DATABASE_URL (драйвер postgresql+psycopg) и выполните `make test PYTEST_WORKERS=0`. Фикстуры создают и удаляют таблицы: никогда не указывайте рабочую БД! Параллельные workers для общей БД запрещены. CI делает это автоматически через service postgres:15 и временный CI_JOB_TOKEN.

## GitLab и runners

1. Создайте пустой GitLab-проект. Добавьте `git remote add gitlab <SSH_URL_ИЗ_GITLAB>` и отправьте ветку. После ревью и настройки защиты влейте её в main. Bootstrap SHA уже задан в YAML; история обоих коммитов должна попасть в GitLab (не squash первоначальной поставки).
2. Docker executor runner с тегом `lab5-python`: image/services, доступ к PyPI и registry.
3. Shell executor runner на отдельной VM с тегом `lab5-docker`: Bash, git, make, python3, Docker, Compose v2, Buildx. Нужен доступ runner к Docker daemon. Приложения на портах 5000/8080 на VM не должны конфликтовать. Использовать только для доверенного учебного проекта; Docker даёт широкие права на VM.
4. Все Docker jobs используют resource_group lab5-docker-host. Container-check использует уникальный Compose project, а cleanup удаляет только его volume. Не используйте один shell runner для production.
5. Settings → Repository → Branch rules: main, merge Maintainers, прямой push No one, force push запрещён. После bootstrap все изменения только через MR.
6. Settings → Merge requests: минимум 1 approval, обязательный Code Owner, запрет self-approve/approval коммитером, сброс approvals при новых коммитах, Pipelines must succeed. Если редакция не поддерживает обязательных Code Owners, этот пункт пока НЕ выполнен.
7. CI/CD Variables: REGISTRY_PASSWORD — masked+protected; REGISTRY_USER — protected; при внешнем registry LAB_REGISTRY_HOST и LAB_REGISTRY_IMAGE — protected. Не переопределять CI_REGISTRY*. Встроенный registry использует CI_REGISTRY_USER/PASSWORD. DB_PASSWORD нужен только для отдельного окружения, не для тестовой БД. SSH_PRIVATE_KEY в этой ЛР не нужен; если будет deploy, использовать protected File variable, не обещать маскирование многострочного ключа.
8. Job token permissions: минимальный allowlist без чужих проектов. По возможности защитить публикационные теги registry: `needs` не является границей прав против произвольного изменения YAML обладателем права push в registry.
9. Выполнить GitLab CI Lint. Проверить лимит размера artifacts для image.tar.gz. Сначала зелёный MR pipeline, затем main pipeline с publish.

Guard читает доверенную версию скрипта из базы сравнения. При первоначальной поставке без guard в main используется bootstrap-коммит. Это не защита от администратора: YAML/скрипты защищаются Code Owners и ревью. Сам guard проверяет AST/настройки/YAML, но не доказывает отсутствие всех возможных обходов.

## Архитектура pipeline

Ровно восемь стадий: lint → test → migrations → backup → security → container-check → build → publish. Config-guard первый, lint зависит от него. Test и coverage реально подключены к PostgreSQL. БД jobs независимы, поэтому backup сначала повторно применяет миграции и проверяет восстановление. Gitleaks/pip-audit/Trivy fs обязательны. Build сохраняет архив без push, затем Trivy проверяет этот архив. Publish зависит от всех jobs и доступен только для защищённой main. SHA образа связывает образ с коммитом, latest обновляется только если коммит ещё является вершиной main. Кэш pip зависит от requirements; BuildKit использует local cache через `--cache-from`, без ранней публикации cache image.

## Локальный registry

```bash
docker compose -p lab5-registry --profile registry up -d registry
curl --fail http://127.0.0.1:5000/v2/
```

Registry привязан к loopback; минимальный вариант без аутентификации. Переменные логина сами не включают htpasswd. Для HTTP registry Docker может требовать insecure-registries; предпочтительны TLS и аутентификация. Main pipeline по умолчанию публикует во встроенный GitLab Registry, не в localhost. Внешний registry должен быть доступен Docker Engine/Buildx runner; localhost в контейнере не равен localhost VM. Registry запускайте отдельным Compose project, не внутри временного проекта container-check.

## Пять сценариев защиты

Начинать каждую демонстрацию с актуальной main, отдельная ветка, не сливать сломанные изменения.

### 1. Сломанный тест

```bash
git switch main
git switch -c demo/red-test
printf 'def test_lab5_failure():\n    assert 2 + 2 == 5\n' > tests/test_lab5_failure.py
git add tests/test_lab5_failure.py
git commit -m 'demo: failing test'
git push -u gitlab demo/red-test -o merge_request.create -o merge_request.target=main
```

Ожидание: test/coverage красные, последующие jobs заблокированы; JUnit скачивается. Фраза: «Та же команда make test ловит функциональную ошибку; последующие обязательные зависимости не выполнены». Для проверки миграции отдельным MR добавьте ошибку в НОВУЮ миграцию, не редактируйте уже применённую рабочую.

### 2. Искусственный секрет

```bash
git switch main
git switch -c demo/secret
mkdir -p demo
python - <<'PY'
from pathlib import Path
import secrets
Path('demo/secret.txt').write_text('LAB5_DEMO_TOKEN=LAB5_' + secrets.token_hex(16) + '\n')
PY
git add demo/secret.txt
git commit -m 'demo: synthetic secret'
git push -u gitlab demo/secret -o merge_request.create -o merge_request.target=main
```

Ожидание: gitleaks красный, SARIF сохранён. Фраза: «Токен искусственный, встроенные правила сохранены; security нельзя пропустить после успешных тестов». Не сливать ветку: удаление файла не удаляет секрет из истории, Gitleaks сканирует достижимую историю HEAD.

### 3. Удаление тестов

```bash
git switch main
git switch -c demo/delete-test
git rm tests/test_ci_guard.py
git commit -m 'demo: remove tests'
git push -u gitlab demo/delete-test -o merge_request.create -o merge_request.target=main
```

Ожидание: config-guard красный, MR требует Code Owner. Фраза: «Push в feature-ветку разрешён, незаметное слияние tests в main — нет; снижение количества дополнительно блокирует guard».

### 4. Снижение покрытия

```bash
git switch main
git switch -c demo/coverage
python - <<'PY'
from pathlib import Path
p = Path('Makefile')
p.write_text(p.read_text().replace('--cov-fail-under=80', '--cov-fail-under=70'))
PY
git add Makefile
git commit -m 'demo: lower coverage'
git push -u gitlab demo/coverage -o merge_request.create -o merge_request.target=main
```

Ожидание: guard отклоняет снижение; MR требует владельца. Отдельно можно добавить E501 к extend-ignore в .flake8: guard отклонит новый ignore. Фраза: «Зелёный pipeline нельзя получить простым ослаблением quality gate; новый коммит сбрасывает одобрение».

### 5. Корректное изменение

```bash
git switch main
git switch -c demo/green
printf '\nПроверка ЛР5 CI.\n' >> README.md
git add README.md
git commit -m 'docs: CI demo'
git push -u gitlab demo/green -o merge_request.create -o merge_request.target=main
```

Получить независимый approval, дождаться зелёного MR, выполнить merge. Показать main pipeline и registry с полным SHA/latest. Фраза: «В MR публикации нет по политике ветки, на main все проверки повторяются и publish загружает тот же проверенный архив».

В красном feature pipeline publish отсутствует из-за правила ветки, а не только из-за ошибки. Поэтому дополнительно показать полный needs publish на main и отсутствие тега ошибочного SHA. Для буквальной демонстрации skipped publish на красной main используйте отдельный учебный проект, не ослабляйте защиту основной ветки.

## Единый источник истины

Makefile — единый источник истины для make verify и отдельных CI-команд. Одинаковая реализация повышает воспроизводимость и уменьшает «works on my machine». Разработчик может повторить команду до push и доверяет CI. Однако окружение тоже важно: для точного повторения PostgreSQL-тестов нужна отдельная БД. Защита Makefile/конфигураций и обязательное ревью ограничивают обход проверок.

## Чек-лист 16 пунктов

| № | Пункт | Файл/настройка | Показать |
|---|---|---|---|
| 1 | CI выбран | GitLab | Обоснование |
| 2 | Репозиторий/registry | remote, Registry, Compose profile | remote и /v2/ |
| 3 | Push/MR/main | workflow rules | Три вида запуска |
| 4 | Единые команды | Makefile | make в логах |
| 5 | 8 стадий | stages | Граф |
| 6 | Тестовая БД | postgres:15, TEST_DATABASE_URL | Подключение postgres |
| 7 | Отчёты | JUnit/Cobertura/SARIF artifacts | Скачать отчёт |
| 8 | Кэш | pip и BuildKit local | Cache hits |
| 9 | SHA образа | IMAGE_REF | Сравнить с коммитом |
| 10 | Gate публикации | publish needs | Ошибка и отсутствие SHA-тега |
| 11 | Секреты | Variables | Masked/protected без показа значений |
| 12 | Анализаторы | 4 jobs | SARIF/JSON |
| 13 | Защита файлов | CODEOWNERS/guard | Удалить тест |
| 14 | Approvals/branch | GitLab UI | Заблокированный MR |
| 15 | Нельзя ослабить незаметно | Guard+review | Порог 70 отклонён |
| 16 | Красный/зелёный | Demo branches | JUnit и main publish |
