def get_query(person_id):
    query = {
        "bool": {
            "should": [
                {
                    "nested": {
                        "path": "actors",
                        "query": {"term": {"actors.id": person_id}},
                    }
                },
                {
                    "nested": {
                        "path": "writers",
                        "query": {"term": {"writers.id": person_id}},
                    }
                },
                {
                    "nested": {
                        "path": "directors",
                        "query": {"term": {"directors.id": person_id}},
                    }
                },
            ]
        }
    }
    return query
