.PHONY: setup run test quality health verify

PYTHON = python
HEALTH_URL = http://localhost:5000/health

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
	$(PYTHON) -m flake8 --config=setup.cfg app tests run.py
	@echo "Quality check completed successfully."

health:
	@echo "Checking StudentTrack health..."
	@$(PYTHON) -c "import json, urllib.request; r = urllib.request.urlopen('$(HEALTH_URL)'); body = r.read().decode(); print('HTTP status:', r.status); print('Response:', body); assert r.status == 200; assert json.loads(body) == {'status': 'ok'}"
	@echo "Health check completed successfully."

verify: test quality
	@echo "Starting StudentTrack for health check..."
	@$(PYTHON) run.py > .verify-server.log 2>&1 & \
	PID=$$!; \
	sleep 2; \
	$(MAKE) health; \
	STATUS=$$?; \
	kill $$PID 2>/dev/null || true; \
	rm -f .verify-server.log; \
	if [ $$STATUS -ne 0 ]; then exit $$STATUS; fi
	@echo "Full verification completed successfully."