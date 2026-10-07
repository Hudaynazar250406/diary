"""Создание резервной копии БД через docker compose exec pg_dump."""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

DB_SERVICE = "db"
DB_USER = "studenttrack"
DB_NAME = "studenttrack"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_file = BACKUP_DIR / f"backup_{timestamp}.sql"

cmd = [
    "docker", "compose", "exec", "-T", DB_SERVICE,
    "pg_dump", "-U", DB_USER, "-d", DB_NAME,
]

print(f"Backup -> {out_file}")
with open(out_file, "wb") as f:
    result = subprocess.run(cmd, stdout=f, cwd=ROOT)
    if result.returncode != 0:
        print("Backup FAILED", file=sys.stderr)
        sys.exit(1)

size = out_file.stat().st_size
print(f"OK: {out_file.name} ({size} bytes)")