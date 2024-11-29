import uuid
from random import choice

index_ = "persons"


def generate_persons(quantity: int = 1) -> list[dict]:
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
