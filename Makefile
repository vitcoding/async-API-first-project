# http://localhost:8000/api/openapi

up-dc:
	docker compose up -d --build --force-recreate

tests:
	docker compose -f fastapi-solution/tests/functional/docker-compose.yml up -d --build --force-recreate

tests-destroy:
	docker compose -f fastapi-solution/tests/functional/docker-compose.yml down -v

build:
	docker compose -f docker-compose.yml build --force-rm
up:
	docker compose -f docker-compose.yml up -d
start:
	docker compose -f docker-compose.yml start
down:
	docker compose -f docker-compose.yml down
destroy:
	docker compose -f docker-compose.yml down -v
stop:
	docker compose -f docker-compose.yml stop


