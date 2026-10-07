.PHONY: setup run test quality health verify migrate backup restore up down coverage container-check

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

coverage:
	@echo "Running coverage..."
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80 -q
	@echo "Coverage check completed successfully."

verify: test quality coverage
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

container-check:
	@echo "Building containers..."
	docker compose build
	@echo "Starting containers..."
	docker compose up -d
	@echo "Waiting for healthchecks (15s)..."
	@$(PYTHON) -c "import time; time.sleep(15)"
	@echo "Container status:"
	docker compose ps
	@echo "Checking /health..."
	@$(PYTHON) -c "import urllib.request, json; r=urllib.request.urlopen('http://localhost:5000/health'); print('HTTP', r.status, json.loads(r.read().decode())); assert r.status==200"
	@echo "Checking container user (must not be root)..."
	docker compose exec -T web whoami
	@echo "Container check completed successfully."