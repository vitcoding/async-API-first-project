import uuid
from random import choice


def generate_persons(quantity):
    """The function of generating persons for tests."""

    persons = [
        {
            "id": str(uuid.uuid4()),
            "full_name": "John",
            "roles": choice([["Actor"], ["Writer"], ["Director"]]),
            "film_ids": [str(uuid.uuid4()) for _ in range(choice([1, 2, 3]))],
        }
        for _ in range(quantity)
    ]

    return persons
