.PHONY: setup run test quality health verify migrate backup restore up down

PYTHON = python

setup:
	@echo "Installing project dependencies..."
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Setup completed."

run:
	@echo "Starting StudentTrack..."
	$(PYTHON) run.py

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest -v
	@echo "Tests completed successfully."

quality:
	@echo "Running Flake8..."
	$(PYTHON) -m flake8 --config=setup.cfg app tests run.py scripts
	@echo "Quality check completed successfully."

health:
	$(PYTHON) scripts/verify.py

verify: test quality
	$(PYTHON) scripts/verify.py
	@echo "Full verification completed successfully."

migrate:
	@echo "Applying migrations..."
	$(PYTHON) -m flask --app run db upgrade
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