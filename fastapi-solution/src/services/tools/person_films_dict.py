from typing import Any


def films_dict(
    person_id: str, films: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Функция сборки словаря фильмов персоны."""

    films_person = []
    for film in films:
        film_temp, roles_temp = {}, []
        for key, value in dict(film).items():
            match key:
                case "id":
                    film_temp[key] = value
                case "directors" | "actors" | "writers":
                    for item in value:
                        if item["id"] == person_id:
                            roles_temp.append(key[:-1])
        film_temp["roles"] = sorted(roles_temp)

        films_person.append(film_temp)

    return films_person
