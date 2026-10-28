.PHONY: setup run test quality health verify migrate backup restore up down dev-db coverage mutation container-check

PYTHON ?= python
PYTEST_WORKERS ?= auto

setup:
	$(PYTHON) -m pip install -r requirements.txt -r requirements-ci.txt

run:
	$(PYTHON) run.py

test:
	$(PYTHON) -m pytest -v -n $(PYTEST_WORKERS)

quality:
	$(PYTHON) -m flake8 --config=.flake8 app tests run.py scripts

health:
	$(PYTHON) scripts/verify.py

coverage:
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80 -q -n $(PYTEST_WORKERS)

mutation:
	$(PYTHON) -m pytest --gremlins

verify: test quality coverage health

ifeq ($(CI),true)
migrate:
	$(PYTHON) -m flask --app run db upgrade

backup:
	mkdir -p backups
	pg_dump --no-password --format=custom --file=backups/ci.dump

restore:
	test -n "$(DUMP)"
	pg_restore --no-password --clean --if-exists --no-owner --exit-on-error --dbname="$$PGDATABASE" "$(DUMP)"

else
migrate:
	docker compose exec -T --index 1 web python -m flask --app run db upgrade

backup:
	$(PYTHON) scripts/backup.py

restore:
	$(PYTHON) scripts/restore.py

endif

up:
	docker compose up -d

down:
	docker compose down

dev-db:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d db

container-check:
	$(PYTHON) scripts/container_check.py

.PHONY: config-guard security-secrets security-deps security-fs security-image

config-guard:
	$(PYTHON) scripts/check_critical_files.py

security-secrets:
	mkdir -p reports
	gitleaks git . --config=.gitleaks.toml --log-opts=HEAD --redact --report-format=sarif --report-path=reports/gitleaks.sarif --exit-code=1

security-deps:
	mkdir -p reports
	$(PYTHON) -m pip_audit --requirement requirements.txt --format=json --output=reports/pip-audit.json

security-fs:
	mkdir -p reports
	trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --exit-code 1 --format sarif --output reports/trivy-fs.sarif --skip-dirs .git --skip-dirs .cache --skip-dirs .venv --skip-dirs reports .

security-image:
	mkdir -p reports
	trivy image --input image.tar.gz --scanners vuln,secret --severity HIGH,CRITICAL --exit-code 1 --format sarif --output reports/trivy-image.sarif

.PHONY: env-init

# Для первого локального запуска; существующий .env не изменяется.
env-init:
	$(PYTHON) scripts/init_env.py
