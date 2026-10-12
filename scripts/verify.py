"""Кросс-платформенная проверка health-эндпоинта приложения.

Запускает Flask-приложение, ждёт готовности, делает GET /health,
проверяет ответ, останавливает сервер.
Работает в Windows, Linux, macOS.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEALTH_URL = "http://127.0.0.1:5000/health"
TIMEOUT = 15


def wait_for_health():
    start = time.time()
    last_error = None
    while time.time() - start < TIMEOUT:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=1) as r:
                if r.status == 200:
                    body = r.read().decode()
                    data = json.loads(body)
                    if data.get("status") == "ok":
                        print(f"Health check OK: {body}")
                        return True
                    print(f"Unexpected /health response: {body}", file=sys.stderr)
                    return False
        except Exception as e:
            last_error = e
            time.sleep(0.5)
    print(f"Health check failed in {TIMEOUT}s: {last_error}", file=sys.stderr)
    return False


def main():
    env = os.environ.copy()
    env["FLASK_ENV"] = "development"

    print("Starting application...")
    proc = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        if not wait_for_health():
            return 1
        return 0
    finally:
        print("Stopping application...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())