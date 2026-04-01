.PHONY: install run test docker-build docker-up

install:
	pip install -r requirements.txt

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

docker-build:
	docker build -t rpa-freight-bridge:latest .

docker-up:
	docker-compose up -d