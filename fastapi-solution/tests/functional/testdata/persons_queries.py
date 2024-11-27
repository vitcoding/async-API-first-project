persons_search_queries = [
    (
        {"query": "John"},
        {"status": 200, "length": 10, "cashed_data": True},
    ),
    (
        {"query": "James"},
        {"status": 404, "length": 1, "cashed_data": False},
    ),
    (
        {"query": "John", "page_size": 5, "page_number": 1},
        {"status": 200, "length": 5, "cashed_data": True},
    ),
    (
        {"query": "John", "page_size": 5, "page_number": 2},
        {"status": 200, "length": 5, "cashed_data": True},
    ),
    (
        {"query": "John", "page_size": 5, "page_number": 3},
        {"status": 404, "length": 1, "cashed_data": False},
    ),
]
