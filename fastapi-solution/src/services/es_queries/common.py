def get_query(
    page_size: int = None,
    page_number: int = None,
    sort_field: str | None = None,
) -> dict:
    query_body = {}

    if page_size is not None:
        query_body["size"] = page_size

    if page_size is not None and page_number is not None:
        query_body["from"] = (page_number - 1) * page_size

    if sort_field is not None and len(sort_field) > 1:
        order = ("asc", "desc")[sort_field.startswith("-")]
        if order == "desc":
            sort_field = sort_field[1:]

        query_body["sort"] = [
            {
                sort_field: {"order": order, "missing": "_last"},
            }
        ]

    return query_body
