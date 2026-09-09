.PHONY: setup run test health verify

setup:
	python -m venv venv
	. venv/bin/activate; pip install -r requirements.txt
	cp -n .env.example .env || true

run:
	python run.py

test:
	pytest -v

health:
	curl -s http://localhost:5000/health

verify: test
	@echo "Все локальные проверки пройдены"
