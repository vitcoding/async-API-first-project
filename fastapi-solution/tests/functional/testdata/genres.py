import uuid
from random import choice


def generate_genres(quantity):
    genres = [
        {
            "id": str(uuid.uuid4()),
            "name": choice(("Action", "Sci-Fi", "Drama")),
            "description": None,
        }
        for _ in range(quantity)
    ]

    return genres
