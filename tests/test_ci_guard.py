"""Регрессионные тесты контроля конфигурации CI."""
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('guard', ROOT / 'scripts/check_critical_files.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def test_ast_counts_async_and_regular_tests():
    assert guard.count_tests('def test_a(): pass\nasync def test_b(): pass\ndef helper(): pass') == 2


def test_guard_accepts_current_ci():
    assert guard.check_ci((ROOT / '.gitlab-ci.yml').read_text())['stages'] == guard.STAGES


def test_guard_rejects_missing_stage():
    text = (ROOT / '.gitlab-ci.yml').read_text().replace('  - security\n', '')
    with pytest.raises(ValueError):
        guard.check_ci(text)


def test_guard_rejects_allowed_failure():
    text = (ROOT / '.gitlab-ci.yml').read_text().replace('  stage: security\n',
                                                         '  stage: security\n  allow_failure: true\n', 1)
    with pytest.raises(ValueError):
        guard.check_ci(text)


def test_guard_rejects_optional_needs():
    text = (ROOT / '.gitlab-ci.yml').read_text().replace(
        '    - {job: test, artifacts: false}', '    - {job: test, artifacts: false, optional: true}')
    with pytest.raises(ValueError):
        guard.check_ci(text)


def test_guard_rejects_new_linter_ignore():
    with pytest.raises(ValueError):
        guard.check_flake8('[flake8]\nignore=E203\n', '[flake8]\nignore=E203,E501\n')


def test_guard_reads_coverage_threshold():
    assert guard.thresholds('Makefile', 'pytest --cov-fail-under=80') == [80.0]


def test_guard_ignores_commented_threshold():
    assert guard.thresholds('Makefile', '# pytest --cov-fail-under=100\npytest --cov-fail-under=70') == [70.0]


def test_guard_rejects_removed_flake8_section():
    with pytest.raises(ValueError):
        guard.check_flake8('[flake8]\nignore=E203\n', '[other]\nvalue=1\n')
