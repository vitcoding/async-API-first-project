run_main = python main.py

install:
	pip install -r requirements.txt

run:
	$(run_main)

run-dev:
	export APP_ENV=dev; \
	$(run_main)

run-doc:
	export APP_ENV=docker; \
	$(run_main)

json-rm:
	rm data/data_state.json

es-rm: json-rm
	curl -X DELETE http://localhost:9200/movies

query_all:
	curl -X GET http://localhost:9200/movies/_search 

