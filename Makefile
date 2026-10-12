.PHONY: setup run test quality health verify migrate backup restore up down dev-db coverage container-check

PYTHON = python

setup:
	@echo "Installing project dependencies..."
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Setup completed."

run:
	@echo "Starting StudentTrack..."
	$(PYTHON) run.py

test:
	@echo "Running tests in parallel..."
	$(PYTHON) -m pytest -v -n auto
	@echo "Tests completed successfully."

quality:
	@echo "Running Flake8..."
	$(PYTHON) -m flake8 --config=setup.cfg app tests run.py scripts
	@echo "Quality check completed successfully."

health:
	$(PYTHON) scripts/verify.py

coverage:
	@echo "Running coverage..."
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80 -q -n auto
	@echo "Coverage check completed successfully."

verify: test quality coverage
	$(PYTHON) scripts/verify.py
	@echo "Full verification completed successfully."

migrate:
	@echo "Applying migrations in container..."
	docker compose exec -T --index 1 web python -m flask --app run db upgrade
	@echo "Migrations applied."

backup:
	@echo "Backing up DB..."
	$(PYTHON) scripts/backup.py

restore:
	@echo "Restoring DB..."
	$(PYTHON) scripts/restore.py

up:
	docker compose up -d

down:
	docker compose down

dev-db:
	@echo "Starting dev DB with published port 5432 (local development)..."
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d db

container-check:
	@echo "Running container environment checks..."
	$(PYTHON) scripts/container_check.py
	@echo "Container check completed successfully."
