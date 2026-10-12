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
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "http://127.0.0.1:8080"
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


def run(cmd, capture=True):
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=capture,
        text=True,
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
        pinned = bool(image) and ":" in image and not image.endswith(":latest")
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
    check("запущено минимум два экземпляра web", replicas >= 2, f"replicas={replicas}")

    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    users = re.findall(r"^USER\s+(\S+)", dockerfile, flags=re.MULTILINE)
    check("Dockerfile: приложение не от root",
          bool(users) and users[-1] not in ("root", "0"),
          f"USER {users[-1]}" if users else "USER не найден")


def check_build_and_up():
    print("2. Сборка и запуск")
    r = compose("build")
    check("сборка образа", r.returncode == 0)
    if r.returncode != 0:
        print(r.stdout[-4000:] + r.stderr[-2000:], file=sys.stderr)
        return False

    r = compose("up", "-d")
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
    compose("up", "-d")
    check("экземпляр восстановлен", wait_all_healthy(HEALTH_TIMEOUT))


def main():
    print("=== Контейнерная проверка StudentTrack ===")
    check_static_config()
    if failures:
        return 1
    if not check_build_and_up():
        return 1
    check_http()
    check_non_root()
    check_failover()

    print()
    if failures:
        print("ПРОВЕРКА НЕ ПРОЙДЕНА:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("Все проверки контейнерного окружения пройдены.")
    return 0


if __name__ == "__main__":
    # Корректный вывод кириллицы в консоли Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
