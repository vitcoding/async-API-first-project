from pydantic import BaseModel

# from uuid import UUID


class Film(BaseModel):
    id: str
    imdb_rating: float
    genres: list
    title: str
    description: str
    directors_names: list
    actors_names: list
    writers_names: list
    directors: list
    actors: list
    writers: list
