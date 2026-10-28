"""Проверки безопасной подготовки локального окружения."""
import importlib.util
from pathlib import Path
import stat

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('init_env', ROOT / 'scripts/init_env.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def env_root(tmp_path):
    (tmp_path / '.env.example').write_text(
        'DATABASE_URL=\nPOSTGRES_USER=studenttrack\nPOSTGRES_PASSWORD=\nSECRET_KEY=\n', encoding='utf-8')
    return tmp_path


def test_env_contains_generated_secrets(env_root):
    target = module.init_env(env_root)
    values = dict(line.split('=', 1) for line in target.read_text().splitlines())
    assert len(values['POSTGRES_PASSWORD']) == 48
    assert len(values['SECRET_KEY']) == 64
    assert values['DATABASE_URL'] == ''
    assert values['POSTGRES_USER'] == 'studenttrack'


def test_existing_env_is_never_overwritten(env_root):
    target = env_root / '.env'
    target.write_text('existing-data', encoding='utf-8')
    with pytest.raises(FileExistsError):
        module.init_env(env_root)
    assert target.read_text() == 'existing-data'


def test_missing_required_variables_does_not_create_env(env_root):
    (env_root / '.env.example').write_text('SECRET_KEY=\n', encoding='utf-8')
    with pytest.raises(ValueError):
        module.init_env(env_root)
    assert not (env_root / '.env').exists()


def test_duplicate_variable_does_not_create_env(env_root):
    with (env_root / '.env.example').open('a') as stream:
        stream.write('SECRET_KEY=\n')
    with pytest.raises(ValueError):
        module.init_env(env_root)
    assert not (env_root / '.env').exists()


@pytest.mark.skipif(__import__('os').name == 'nt', reason='POSIX permissions')
def test_env_is_private_on_posix(env_root):
    target = module.init_env(env_root)
    assert stat.S_IMODE(target.stat().st_mode) == 0o600


def test_generated_secrets_are_different(env_root, tmp_path_factory):
    other = tmp_path_factory.mktemp('other-env')
    (other / '.env.example').write_text((env_root / '.env.example').read_text(), encoding='utf-8')
    assert module.init_env(env_root).read_text() != module.init_env(other).read_text()
