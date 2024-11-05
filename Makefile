
# http://localhost:8000/api/openapi
run-api:
	fastapi dev fastapi-solution/src/main.py
# fastapi run fastapi-solution/src/main.py

up-dc:
	docker compose up -d --build --force-recreate

down-dc:
	docker compose down

down-dc-v:
	docker compose down -v