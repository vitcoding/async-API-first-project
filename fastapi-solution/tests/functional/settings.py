from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    # es_host: str = Field("http://127.0.0.1:9200", env="ELASTIC_HOST")
    es_host: str = Field("http://localhost:9200", env="ELASTIC_HOST")
    es_index: str = "movies"
    es_id_field: str = Field("id", env="ES_ID_FIELD")
    es_index_mapping: dict = Field(
        {
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
                    # "created_at": {"type": "date"},
                    # "updated_at": {"type": "date"},
                    # "film_work_type": {"type": "keyword"},
                }
            }
        }
    )
    # es_index_mapping: dict = Field(
    #     {
    #         "mappings": {
    #             "properties": {
    #                 "id": {"type": "keyword"},
    #                 "imdb_rating": {"type": "float"},
    #                 "genres": {"type": "keyword"},
    #                 "title": {
    #                     "type": "text",
    #                     "analyzer": "ru_en",
    #                     "fields": {"raw": {"type": "keyword"}},
    #                 },
    #                 "description": {"type": "text", "analyzer": "ru_en"},
    #                 "directors_names": {"type": "text", "analyzer": "ru_en"},
    #                 "actors_names": {"type": "text", "analyzer": "ru_en"},
    #                 "writers_names": {"type": "text", "analyzer": "ru_en"},
    #                 "directors": {
    #                     "type": "nested",
    #                     "dynamic": "strict",
    #                     "properties": {
    #                         "id": {"type": "keyword"},
    #                         "name": {"type": "text", "analyzer": "ru_en"},
    #                     },
    #                 },
    #                 "actors": {
    #                     "type": "nested",
    #                     "dynamic": "strict",
    #                     "properties": {
    #                         "id": {"type": "keyword"},
    #                         "name": {"type": "text", "analyzer": "ru_en"},
    #                     },
    #                 },
    #                 "writers": {
    #                     "type": "nested",
    #                     "dynamic": "strict",
    #                     "properties": {
    #                         "id": {"type": "keyword"},
    #                         "name": {"type": "text", "analyzer": "ru_en"},
    #                     },
    #                 },
    #             }
    #         }
    #     }
    # )

    redis_host: str = Field("http://localhost:6379", env="REDIS_HOST")
    # service_url: str = Field("localhost:8000", env="SERVICE_URL")
    service_url: str = Field("http://localhost:8000", env="SERVICE_URL")


test_settings = TestSettings()
