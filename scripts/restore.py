"""Восстановление БД из резервной копии через docker compose exec psql."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = ROOT / "backups"

DB_SERVICE = "db"
DB_USER = "studenttrack"
DB_NAME = "studenttrack"

if len(sys.argv) > 1:
    dump_file = Path(sys.argv[1])
else:
    files = sorted(BACKUP_DIR.glob("backup_*.sql"))
    if not files:
        print("No backups found in backups/", file=sys.stderr)
        sys.exit(1)
    dump_file = files[-1]

if not dump_file.exists():
    print(f"File not found: {dump_file}", file=sys.stderr)
    sys.exit(1)

print(f"Restore <- {dump_file.name}")

# 1. Сбрасываем схему
drop_cmd = [
    "docker", "compose", "exec", "-T", DB_SERVICE,
    "psql", "-U", DB_USER, "-d", DB_NAME,
    "-c", "DROP SCHEMA public CASCADE; CREATE SCHEMA public;",
]
r = subprocess.run(drop_cmd, cwd=ROOT)
if r.returncode != 0:
    print("Drop schema FAILED", file=sys.stderr)
    sys.exit(1)

# 2. Заливаем дамп
restore_cmd = [
    "docker", "compose", "exec", "-T", DB_SERVICE,
    "psql", "-U", DB_USER, "-d", DB_NAME,
]
with open(dump_file, "rb") as f:
    r = subprocess.run(restore_cmd, stdin=f, cwd=ROOT)
    if r.returncode != 0:
        print("Restore FAILED", file=sys.stderr)
        sys.exit(1)

print("OK: restored")