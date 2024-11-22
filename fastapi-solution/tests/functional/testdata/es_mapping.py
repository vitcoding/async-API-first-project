MOVIES_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "imdb_rating": {"type": "float"},
            "title": {"type": "text"},
            "description": {"type": "text"},
            "genres": {"type": "text"},
            "directors_names": {"type": "text"},
            "actors_names": {"type": "text"},
            "writers_names": {"type": "text"},
            "directors": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text"},
                },
            },
            "actors": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text"},
                },
            },
            "writers": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text"},
                },
            },
        }
    }
}

GENRES_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "name": {"type": "text"},
            "description": {"type": "text"},
        }
    }
}
