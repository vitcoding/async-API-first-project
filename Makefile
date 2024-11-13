# http://localhost:8000/api/openapi
up-dc:
	docker compose up -d --build --force-recreate

down-dc:
	docker compose down

down-dc-v:
	docker compose down -v


build:
	docker-compose -f docker-compose.yml build --force-rm
build-local:
	docker-compose -f docker-compose-local.yml build --force-rm
up:
	docker-compose -f docker-compose.yml up -d
up-local:
	docker-compose -f docker-compose-local.yml up -d
start:
	docker-compose -f docker-compose.yml start
start-local:
	docker-compose -f docker-compose-local.yml start
down:
	docker-compose -f docker-compose.yml down
down-local:
	docker-compose -f docker-compose-local.yml down
destroy:
	docker-compose -f docker-compose.yml down -v
destroy-local:
	docker-compose -f docker-compose-local.yml down -v
stop:
	docker-compose -f docker-compose.yml stop
stop-local:
	docker-compose -f docker-compose-local.yml v



