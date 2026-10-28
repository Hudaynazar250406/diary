"""Создаёт локальный .env из примера, не перезаписывая существующий файл."""
import os
from pathlib import Path
import secrets


ROOT = Path(__file__).resolve().parents[1]


def init_env(root=ROOT):
    root = Path(root)
    target = root / '.env'
    if target.exists():
        raise FileExistsError('.env уже существует; существующие секреты сохранены')
    template = (root / '.env.example').read_text(encoding='utf-8')
    replacements = {
        'POSTGRES_PASSWORD': secrets.token_hex(24),
        'SECRET_KEY': secrets.token_hex(32),
    }
    seen = set()
    lines = []
    for line in template.splitlines():
        key, separator, _ = line.partition('=')
        if separator and key in replacements:
            if key in seen:
                raise ValueError(f'Повторяющаяся переменная в .env.example: {key}')
            seen.add(key)
            line = f'{key}={replacements[key]}'
        lines.append(line)
    if seen != set(replacements):
        raise ValueError('В .env.example отсутствуют POSTGRES_PASSWORD или SECRET_KEY')
    # O_EXCL предотвращает перезапись даже при одновременном запуске.
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write('\n'.join(lines) + '\n')
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    return target


if __name__ == '__main__':
    try:
        path = init_env()
    except (OSError, ValueError) as error:
        raise SystemExit(f'ENV-INIT: {error}')
    print(f'ENV-INIT: создан {path.name}; секреты не выводятся в журнал')
