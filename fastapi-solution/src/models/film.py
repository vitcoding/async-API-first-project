from pydantic import BaseModel

# from uuid import UUID


class Film(BaseModel):
    # Надо будет добавить трансформацию в кэш для id (пока str)
    id: str
    imdb_rating: float
    genres: list
    title: str
    description: str | None
    directors_names: list
    actors_names: list
    writers_names: list
    directors: list
    actors: list
    writers: list
