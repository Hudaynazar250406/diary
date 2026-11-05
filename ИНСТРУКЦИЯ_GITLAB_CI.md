# Инструкция: локальный GitLab CI/CD

## Доступ

- GitLab: `http://localhost:8929`
- Проект: `http://localhost:8929/root/diary`
- SSH Git URL: `ssh://git@localhost:2222/root/diary.git`
- Локальный registry: `localhost:5050` (контейнер `registry`, образ `registry:2`,
  volume `registry_data`; запуск: `docker start registry`)
- Ветка CI: `chore/local-gitlab-ci`
- Runner tags: `lab5-python`, `lab5-docker`

Начальный пароль пользователя `root` хранится только внутри Docker volume:

```bash
docker exec gitlab cat /etc/gitlab/initial_root_password
```

## Запуск и остановка GitLab

```bash
cd C:/Users/User/gitlab-local
docker compose up -d
docker compose ps
docker compose logs -f gitlab
docker compose stop
```

Не удаляйте volumes `gitlab_config`, `gitlab_logs` и `gitlab_data`.

## Runner-ы

```bash
cd C:/Users/User/gitlab-local/runners
docker compose up -d
docker compose ps
docker logs -f gitlab-runner-python
docker logs -f gitlab-runner-docker
```

- `lab5-python` использует Docker executor и Python-образы.
- `lab5-docker` использует Shell executor, Docker CLI, Compose, Buildx, Make и Python.
- Runner-ы привязаны к приватному проекту `root/diary` и выполняют только tagged jobs.

Оба Runner-а используют Docker socket хоста. Не подключайте к ним недоверенные проекты.

## Работа с проектом

```bash
cd C:/Users/User/Desktop/DEVOPS/diary
git switch chore/local-gitlab-ci
git remote -v
git status
```

GitHub remote называется `origin`; локальный GitLab remote — `gitlab`.
Не выполняйте `push` в `main` или `origin` без отдельного решения.

После commit отправьте ветку в GitLab:

```bash
git push gitlab chore/local-gitlab-ci
```

## Pipeline

Файл `.gitlab-ci.yml` выполняет этапы:

1. lint;
2. test;
3. migrations;
4. backup;
5. security;
6. container-check;
7. build;
8. publish.

`publish` запускается только для push в `main`. На feature-ветках образ не публикуется.

В GitLab откройте проект → **Build → Pipelines**, чтобы посмотреть pipeline,
логи jobs и artifacts. Для CI-файла доступны отчёты JUnit, Cobertura и SARIF.

## Локальная проверка

```bash
python -m pytest -q
git diff --check
bash scripts/check_critical_files.sh
```

Перед commit проверьте:

```bash
git status
git diff --cached
```

Не добавляйте `.env`, пароли, API-токены, SSH-ключи, дампы базы данных и файлы
из локальных Docker volumes.

## Остановка всего контура

```bash
cd C:/Users/User/gitlab-local/runners
docker compose stop

cd C:/Users/User/gitlab-local
docker compose stop

docker stop registry
```

Для обычной остановки используйте `stop`, а не удаление volumes: volumes содержат
проекты, настройки GitLab и конфигурации Runner-ов.

## Диагностика

- `HTTP Basic: Access denied` при push — протухли учётные данные в Windows
  Credential Manager; обновить через `git credential reject` + токен root.
- Job падает с `timeout awaiting response headers` при pull образа — сеть до
  Docker Hub нестабильна; у runner'ов стоит `pull_policy = "if-not-present"`,
  достаточно повторить job.
- Job «завис» в статусе running после перезапуска runner — снять через
  `gitlab-rails runner 'Ci::Build.find(ID).drop!'` и повторить pipeline.
