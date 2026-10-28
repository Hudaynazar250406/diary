"""Контроль ослабления тестов, линтера, покрытия и обязательных jobs."""
import ast
import configparser
import os
from pathlib import Path
import re
import subprocess
import tomllib

import yaml


STAGES = ['lint', 'test', 'migrations', 'backup', 'security', 'container-check', 'build', 'publish']
JOBS = {
    'config-guard': 'lint', 'lint': 'lint', 'test': 'test', 'coverage': 'test', 'health': 'test',
    'migrations': 'migrations', 'backup': 'backup', 'gitleaks': 'security', 'pip-audit': 'security',
    'trivy-fs': 'security', 'container-check': 'container-check', 'build': 'build',
    'trivy-image': 'build', 'publish': 'publish',
}
COMMANDS = {
    'lint': 'quality', 'test': 'test', 'coverage': 'coverage', 'health': 'health',
    'migrations': 'migrate', 'backup': 'backup', 'gitleaks': 'security-secrets',
    'pip-audit': 'security-deps', 'trivy-fs': 'security-fs',
    'container-check': 'container-check', 'trivy-image': 'security-image',
}


class Loader(yaml.SafeLoader):
    """Разрешает служебный тег GitLab без исполнения Python."""


Loader.add_constructor('!reference', lambda loader, node: loader.construct_sequence(node))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def count_tests(text):
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_')
        for node in ast.walk(ast.parse(text))
    )


def check_flake8(old, new):
    before = configparser.ConfigParser(interpolation=None)
    after = configparser.ConfigParser(interpolation=None)
    before.read_string(old)
    after.read_string(new)
    for key in ('ignore', 'extend-ignore'):
        a = set(re.split(r'[\s,]+', before.get('flake8', key, fallback=''))) - {''}
        b = set(re.split(r'[\s,]+', after.get('flake8', key, fallback=''))) - {''}
        require(not b - a, f'новые {key}: {sorted(b - a)}')
    for key in ('per-file-ignores', 'exclude', 'extend-exclude', 'select', 'extend-select'):
        require(before.get('flake8', key, fallback='') == after.get('flake8', key, fallback=''),
                f'изменена политика {key}')
    require(after.getint('flake8', 'max-line-length', fallback=79)
            <= before.getint('flake8', 'max-line-length', fallback=79), 'увеличен max-line-length')


def thresholds(name, text):
    if not text:
        return []
    if name == 'Makefile':
        active = '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('#'))
        return [float(x) for x in re.findall(r'--cov-fail-under(?:\s*=\s*|\s+)(\d+(?:\.\d+)?)', active)]
    if name == 'pyproject.toml':
        value = tomllib.loads(text).get('tool', {}).get('coverage', {}).get('report', {}).get('fail_under')
        return [] if value is None else [float(value)]
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(text)
    return [parser.getfloat('coverage:report', 'fail_under')] if parser.has_option(
        'coverage:report', 'fail_under') else []


def check_ci(text):
    ci = yaml.load(text, Loader=Loader)
    require(isinstance(ci, dict) and ci.get('stages') == STAGES, 'нарушен состав/порядок stages')
    require(not re.search(r'^\s*#\s*stage\s*:', text, re.M), 'закомментирован stage')
    for name, stage in JOBS.items():
        job = ci.get(name, {})
        require(job.get('stage') == stage, f'{name}: отсутствует job или изменена стадия')
        require(job.get('allow_failure', False) is False, f'{name}: запрещён allow_failure')
        require(job.get('when') not in ('manual', 'never'), f'{name}: обязательная job отключена')
        for rule in job.get('rules', []):
            require(rule.get('allow_failure', False) is False, f'{name}: allow_failure в rules')
        if name in COMMANDS:
            script = job.get('script', [])
            script = [script] if isinstance(script, str) else script
            active = '\n'.join(line for cmd in script if isinstance(cmd, str) for line in cmd.splitlines()
                               if not line.lstrip().startswith('#'))
            require(re.search(r'\bmake\s+' + re.escape(COMMANDS[name]) + r'(?:\s|$)', active),
                    f'{name}: удалён make {COMMANDS[name]}')
    needs = ci['publish'].get('needs', [])
    names = {item if isinstance(item, str) else item.get('job') for item in needs}
    require(set(JOBS) - {'publish'} <= names, 'publish: неполный needs')
    require(not any(isinstance(item, dict) and item.get('optional') for item in needs),
            'publish: запрещён optional needs')
    return ci


def main():
    root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
    os.chdir(root)
    base = os.getenv('GUARD_BASE_SHA', 'origin/main')

    def old(path):
        result = subprocess.run(['git', 'show', f'{base}:{path}'], text=True, capture_output=True)
        return result.stdout if result.returncode == 0 else None

    subprocess.run(['git', 'cat-file', '-e', f'{base}^{{commit}}'], check=True, capture_output=True)
    baseline = int(Path('.ci/test_baseline').read_text().strip())
    old_baseline = old('.ci/test_baseline')
    # ДОПУЩЕНИЕ: baseline отсутствует только на первоначальном bootstrap.
    previous_baseline = int(old_baseline.strip()) if old_baseline else 0
    require(baseline >= previous_baseline, 'уменьшен baseline')
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', base, '--', 'tests'], text=True)
    previous = sum(count_tests(old(name)) for name in paths.splitlines()
                   if Path(name).name.startswith('test_') and name.endswith('.py'))
    current = sum(count_tests(path.read_text()) for path in Path('tests').rglob('test_*.py'))
    require(current >= max(baseline, previous, previous_baseline),
            f'уменьшено число тестов: сейчас {current}, было {previous}, baseline {baseline}')
    print(f'CONFIG-GUARD: тестовых функций {current}, в базе {previous}, baseline {baseline}')
    for name in ('.flake8', 'setup.cfg'):
        before = old(name)
        if name == '.flake8' and before is None:
            before = old('setup.cfg')
        require(Path(name).exists(), f'удалён {name}')
        if before is not None:
            check_flake8(before, Path(name).read_text())
    for name in ('Makefile', 'pyproject.toml', 'setup.cfg'):
        before = thresholds(name, old(name))
        now = thresholds(name, Path(name).read_text() if Path(name).exists() else None)
        if before or name == 'Makefile':
            require(now and min(now) >= max([80.0, *before]), f'{name}: снижен/удалён порог coverage')
    check_ci(Path('.gitlab-ci.yml').read_text())
    print('CONFIG-GUARD: критический контур не ослаблен')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, SyntaxError, yaml.YAMLError, configparser.Error) as error:
        raise SystemExit(f'CONFIG-GUARD: ОШИБКА: {error}')
