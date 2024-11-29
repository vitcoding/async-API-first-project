from http import HTTPStatus

persons_search_queries = [
    (
        {"query": "John"},
        {"status": HTTPStatus.OK, "length": 10, "cashed_data": True},
    ),
    (
        {"query": "James"},
        {"status": HTTPStatus.NOT_FOUND, "length": 1, "cashed_data": False},
    ),
    (
        {"query": "John", "page_size": 5, "page_number": 1},
        {"status": HTTPStatus.OK, "length": 5, "cashed_data": True},
    ),
    (
        {"query": "John", "page_size": 5, "page_number": 2},
        {"status": HTTPStatus.OK, "length": 5, "cashed_data": True},
    ),
    (
        {"query": "John", "page_size": 5, "page_number": 3},
        {"status": HTTPStatus.NOT_FOUND, "length": 1, "cashed_data": False},
    ),
]
