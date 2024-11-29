from http import HTTPStatus

genres_queries = [
    ({}, {"status": HTTPStatus.OK, "length": 10, "cashed_data": True}),
    (
        {"page_size": 7},
        {"status": HTTPStatus.OK, "length": 7, "cashed_data": True},
    ),
    (
        {"page_size": 0},
        {
            "status": HTTPStatus.UNPROCESSABLE_ENTITY,
            "length": 1,
            "cashed_data": False,
        },
    ),
    (
        {"page_number": 2},
        {"status": HTTPStatus.NOT_FOUND, "length": 1, "cashed_data": False},
    ),
]
