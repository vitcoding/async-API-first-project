import uuid
from random import random, randrange


def generate_films(quantity):
    films = [
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": round(random() * 10, 1),
            "genres": ["Action", "Sci-Fi"],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Stan"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [
                {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"},
                {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "name": "Bob"},
            ],
            "actors": [
                {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"},
                {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "name": "Bob"},
            ],
            "writers": [
                {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
                {
                    "id": "b45bd7bc-2e16-46d5-b125-983d356768c6",
                    "name": "Howard",
                },
            ],
        }
        for _ in range(quantity)
    ]

    return films
