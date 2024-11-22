genres_queries = [
    ({}, {"status": 200, "length": 10, "cashed_data": True}),
    (
        {"page_size": 7},
        {"status": 200, "length": 7, "cashed_data": True},
    ),
    ({"page_size": 0}, {"status": 422, "length": 1, "cashed_data": False}),
    (
        {"page_number": 2},
        {"status": 404, "length": 1, "cashed_data": False},
    ),
]
