from typing import Any
from uuid import UUID

from dateutil.parser import parse


def validate_data(row: dict[str, Any]) -> dict[str, Any]:
    """Функция валидации данных."""

    transformed_row = {}
    for key, value in dict(row).items():
        match key:
            case "id" | "fw_id" | "g_id" | "p_id":
                if isinstance(value, str):
                    value = UUID(value)
            case "creation_date":
                if isinstance(value, str):
                    value = parse(value)
            case (
                "created"
                | "modified"
                | "g_created"
                | "g_modified"
                | "p_created"
                | "p_modified"
            ):
                if isinstance(value, str):
                    value = parse(value)
            case _:
                key = key
                value = value

        transformed_row[key] = value
    return transformed_row
