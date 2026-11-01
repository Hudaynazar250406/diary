"""Автоматическая проверка контейнерного окружения (make container-check).

Проверяет эксплуатационные требования ЛР4:
1. Статическая конфигурация:
   - тегов `latest` нет, все образы запинованы;
   - порт БД не публикуется, приложение недоступно с хоста напрямую;
   - healthcheck есть у каждого сервиса;
   - сеть окружения внутренняя (internal);
   - Dockerfile запускает приложение от непривилегированного пользователя.
2. Сборка образа и запуск окружения.
3. Доступность сервиса через Nginx (порт 8080).
4. Балансировка: запросы попадают минимум на два разных экземпляра web.
5. Процесс веб-приложения работает не от root.
6. Отказоустойчивость: остановка одного экземпляра не прерывает обслуживание,
   при этом контейнер завершается по SIGTERM с кодом 0.

Любое изменение контейнерного окружения принимается только при успешном
выполнении этой команды (см. CONTRIBUTING.md).
"""
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = ""
HEALTH_TIMEOUT = 180
FAILOVER_TIMEOUT = 30

failures = []


def parse_compose_ps(stdout):
    """`docker compose ps --format json` в зависимости от версии возвращает
    JSON-массив или NDJSON (по объекту на строку) — поддерживаем оба."""
    text = stdout.strip()
    if not text:
        return []
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]


def run(cmd, capture=True, env=None):
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=capture,
        text=True,
        env=env,
    )


def compose(*args):
    return run(["docker", "compose", *args])


def check(name, ok, detail=""):
    mark = "OK" if ok else "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"  [{mark}] {name}{suffix}")
    if not ok:
        failures.append(f"{name}{suffix}")


def get(url, timeout=3):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode())


def wait_all_healthy(timeout):
    """Ждёт, пока все контейнеры проекта станут running/healthy."""
    deadline = time.time() + timeout
    last = ""
    while time.time() < deadline:
        r = compose("ps", "--format", "json")
        if r.returncode == 0 and r.stdout.strip():
            containers = parse_compose_ps(r.stdout)
            if containers:
                bad = [
                    f"{c['Service']}:{c.get('State')}:{c.get('Health', '')}"
                    for c in containers
                    if c.get("State") != "running"
                    or c.get("Health", "") not in ("healthy", "")
                ]
                if not bad:
                    return True
                last = ", ".join(bad)
        time.sleep(2)
    print(f"    (последнее состояние: {last})", file=sys.stderr)
    return False


def check_static_config():
    print("1. Статическая конфигурация")
    r = compose("config", "--format", "json")
    check("docker compose config разбирается", r.returncode == 0)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return

    config = json.loads(r.stdout)
    services = config["services"]

    for name, svc in services.items():
        image = svc.get("image", "")
        digest_pinned = "@sha256:" in image and bool(
            re.search(r"@sha256:[0-9a-f]{64}$", image)
        )
        pinned = bool(image) and not image.endswith(":latest") and (
            digest_pinned or bool(svc.get("build"))
        )
        check(f"образ {name} запинован (не latest)", pinned, image or "нет image")
        hc = svc.get("healthcheck", {})
        hc_ok = bool(hc.get("test")) and not hc.get("disable", False)
        check(f"healthcheck у {name} включён", hc_ok)

    db = services.get("db", {})
    check("порт БД не публикуется", not db.get("ports"))

    web = services.get("web", {})
    check("прямой доступ к web с хоста закрыт", not web.get("ports"))

    nginx = services.get("nginx", {})
    nginx_ports = nginx.get("ports", [])
    check("опубликован только порт nginx", len(nginx_ports) == 1,
          str(nginx_ports))

    network = config.get("networks", {}).get("backend", {})
    check("сеть backend внутренняя (internal)", bool(network.get("internal")))

    replicas = web.get("deploy", {}).get("replicas", 1)
    check("настроены минимум две реплики web", replicas >= 2, f"replicas={replicas}")

    for name, svc in services.items():
        limits = svc.get("deploy", {}).get("resources", {}).get("limits", {})
        check(f"лимиты CPU и памяти заданы для {name}",
              bool(limits.get("cpus")) and bool(limits.get("memory")))

    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    users = re.findall(r"^USER\s+(\S+)", dockerfile, flags=re.MULTILINE)
    check("Dockerfile: приложение не от root",
          bool(users) and users[-1] not in ("root", "0"),
          f"USER {users[-1]}" if users else "USER не найден")

    base_images = re.findall(r"^FROM\s+(\S+)", dockerfile, flags=re.MULTILINE)
    check("базовые образы Dockerfile закреплены digest",
          bool(base_images) and all(
              re.search(r"@sha256:[0-9a-f]{64}$", image) for image in base_images
          ))

    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
    check("секретные env-файлы исключены из build context",
          ".env" in dockerignore and ".env.*" in dockerignore)

    lock_lines = (ROOT / "requirements-prod.lock").read_text(
        encoding="utf-8"
    ).splitlines()
    check("production dependencies полностью запинованы",
          bool(lock_lines) and all(
              line.strip() and "==" in line and not line.lstrip().startswith("#")
              for line in lock_lines
          ))

    nginx_config = (ROOT / "nginx" / "nginx.conf").read_text(encoding="utf-8")
    check("Nginx настроен на retry и rate limit",
          "proxy_next_upstream" in nginx_config and "limit_req" in nginx_config)


def check_build_and_up():
    print("2. Сборка и запуск")
    r = compose("build")
    check("сборка образа", r.returncode == 0)
    if r.returncode != 0:
        print(r.stdout[-4000:] + r.stderr[-2000:], file=sys.stderr)
        return False

    image = compose("config", "--format", "json")
    image_name = json.loads(image.stdout)["services"]["web"]["image"]
    inspected = run([
        "docker", "image", "inspect", image_name,
        "--format", "{{json .Config.Env}}",
    ])
    image_environment = inspected.stdout
    secrets_absent = inspected.returncode == 0 and all(
        secret not in image_environment
        for secret in (os.environ["POSTGRES_PASSWORD"], os.environ["SECRET_KEY"])
    )
    check("секреты не встроены в образ", secrets_absent)
    if not secrets_absent:
        return False

    r = compose("up", "-d", "--scale", "web=2")
    check("запуск окружения", r.returncode == 0)
    if r.returncode != 0:
        print(r.stderr[-2000:], file=sys.stderr)
        return False

    check("все контейнеры healthy", wait_all_healthy(HEALTH_TIMEOUT))
    return not failures


def check_http():
    print("3. Доступность и балансировка")
    try:
        status, data = get(f"{BASE_URL}/health")
        check("/health через nginx", status == 200 and data.get("status") == "ok",
              str(data))
    except Exception as e:
        check("/health через nginx", False, str(e))
        return False

    instances = set()
    errors = 0
    for _ in range(12):
        try:
            _, data = get(f"{BASE_URL}/health")
            instances.add(data.get("instance"))
        except Exception:
            errors += 1
    check("запросы обрабатывают минимум два экземпляра",
          len(instances) >= 2 and errors == 0,
          f"экземпляры: {sorted(instances)}")
    return len(instances) >= 2


def check_non_root():
    print("4. Пользователь процесса")
    r = compose("exec", "-T", "--index", "1", "web", "whoami")
    user = r.stdout.strip()
    check("web не от root", r.returncode == 0 and user not in ("root", ""),
          f"whoami -> {user}")


def check_failover():
    print("5. Отказоустойчивость и корректное завершение")
    r = compose("ps", "-q", "web")
    containers = [c for c in r.stdout.split() if c]
    check("найдено минимум два контейнера web", len(containers) >= 2,
          f"{len(containers)} шт.")
    if len(containers) < 2:
        return

    victim = containers[-1]
    run(["docker", "stop", victim])
    code = run(["docker", "inspect", "-f", "{{.State.ExitCode}}", victim])
    check("остановленный экземпляр завершился с кодом 0 (SIGTERM)",
          code.stdout.strip() == "0", code.stdout.strip())

    alive = False
    deadline = time.time() + FAILOVER_TIMEOUT
    attempts = 0
    while time.time() < deadline and attempts < 20:
        attempts += 1
        try:
            status, data = get(f"{BASE_URL}/health", timeout=5)
            if status == 200 and data.get("status") == "ok":
                alive = True
                break
        except Exception:
            time.sleep(1)
    check("сервис доступен после остановки одного экземпляра", alive,
          f"{attempts} попыток")

    # Возвращаем остановленный экземпляр в строй
    compose("up", "-d", "--scale", "web=2")
    check("экземпляр восстановлен", wait_all_healthy(HEALTH_TIMEOUT))


def database_command(sql, *args):
    return compose(
        "exec", "-T", "db", "psql", "-v", "ON_ERROR_STOP=1",
        "-U", os.environ["POSTGRES_USER"], "-d", os.environ["POSTGRES_DB"],
        *args, "-c", sql,
    )


def check_migrations():
    print("6. Миграции")
    result = compose(
        "exec", "-T", "web", "python", "-m", "flask", "--app", "run", "db", "upgrade"
    )
    check("миграции применяются в контейнере", result.returncode == 0,
          result.stderr[-1000:])


def check_persistence():
    print("7. Сохранность данных после пересоздания БД")
    schema = f"container_check_{uuid.uuid4().hex}"
    marker = uuid.uuid4().hex
    created = database_command(
        f'CREATE SCHEMA "{schema}"; CREATE TABLE "{schema}".marker (value text); '
        f'INSERT INTO "{schema}".marker VALUES (\'{marker}\');'
    )
    check("создана временная контрольная запись", created.returncode == 0)
    if created.returncode != 0:
        return

    recreated = compose("up", "-d", "--force-recreate", "db")
    healthy = recreated.returncode == 0 and wait_all_healthy(HEALTH_TIMEOUT)
    check("PostgreSQL пересоздан", healthy)
    read = database_command(
        f'SELECT value FROM "{schema}".marker', "-tA"
    ) if healthy else None
    persisted = read is not None and read.returncode == 0 and read.stdout.strip() == marker
    check("контрольная запись сохранилась в volume", persisted)
    database_command(f'DROP SCHEMA "{schema}" CASCADE')


def check_backup_restore():
    print("8. Резервное копирование и восстановление в новый volume")
    with tempfile.TemporaryDirectory(prefix="studenttrack-backup-") as backup_dir:
        env = os.environ.copy()
        env["BACKUP_DIR"] = backup_dir
        backup = run([sys.executable, str(ROOT / "scripts" / "backup.py")], env=env)
        dump_files = list(Path(backup_dir).glob("backup_*.sql"))
        check("резервная копия создана", backup.returncode == 0 and len(dump_files) == 1,
              backup.stderr[-1000:])
        if backup.returncode != 0 or len(dump_files) != 1:
            return

        removed = compose("down", "-v", "--remove-orphans")
        started = compose("up", "-d", "--scale", "web=2") if removed.returncode == 0 else removed
        healthy = started.returncode == 0 and wait_all_healthy(HEALTH_TIMEOUT)
        check("создано чистое окружение с новым volume", healthy)
        if not healthy:
            return

        restored = run(
            [sys.executable, str(ROOT / "scripts" / "restore.py"), str(dump_files[0])],
            env=env,
        )
        check("дамп восстановлен в новый volume", restored.returncode == 0,
              restored.stderr[-1000:])
        version = database_command("SELECT version_num FROM alembic_version", "-tA")
        check("после восстановления доступны миграции",
              version.returncode == 0 and bool(version.stdout.strip()))


def main():
    print("=== Контейнерная проверка StudentTrack ===")
    os.environ["COMPOSE_PROJECT_NAME"] = f"studenttrack-check-{uuid.uuid4().hex[:10]}"
    with socket.socket() as port_socket:
        port_socket.bind(("127.0.0.1", 0))
        os.environ["NGINX_PORT"] = str(port_socket.getsockname()[1])
    global BASE_URL
    check_host = os.environ.get("CHECK_HOST", "127.0.0.1")
    BASE_URL = f"http://{check_host}:{os.environ['NGINX_PORT']}"
    os.environ["POSTGRES_USER"] = "container_check"
    os.environ["POSTGRES_PASSWORD"] = uuid.uuid4().hex
    os.environ["POSTGRES_DB"] = "container_check"
    os.environ["SECRET_KEY"] = uuid.uuid4().hex
    try:
        check_static_config()
        if not failures and check_build_and_up():
            check_migrations()
            if not failures:
                check_persistence()
            if not failures:
                check_backup_restore()
            if not failures:
                check_http()
                check_non_root()
                check_failover()

        print()
        if failures:
            print("ПРОВЕРКА НЕ ПРОЙДЕНА:", file=sys.stderr)
            for failure in failures:
                print(f"  - {failure}", file=sys.stderr)
            return 1
        print("Все проверки контейнерного окружения пройдены.")
        return 0
    finally:
        compose("down", "-v", "--remove-orphans")


if __name__ == "__main__":
    # Корректный вывод кириллицы в консоли Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
