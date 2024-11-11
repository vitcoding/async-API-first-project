from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.person import PersonService, get_person_service

# from services.persons import PersonListService, get_person_list_service

router = APIRouter()


# Модель ответа API
class Person(BaseModel):
    id: UUID
    full_name: str


# @router.get("")
# async def person_list(
#     page_size: int = Query(50, ge=1),
#     page_number: int = Query(1),
#     person_service: PersonListService = Depends(get_person_list_service),
# ) -> list:
#     persons = await person_service.get_list(page_size, page_number)
#     return [Person(**dict(person)) for person in persons]


# @router.get("/{person_id}/film")
# async def person_film_list(
#     page_size: int = Query(50, ge=1),
#     page_number: int = Query(1),
#     person_service: PersonListService = Depends(get_person_list_service),
# ) -> list:
#     persons = await person_service.get_list(page_size, page_number)
#     return [Person(**dict(person)) for person in persons]


@router.get("/{person_id}", response_model=Person)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="person not found"
        )

    return Person(**dict(person))
