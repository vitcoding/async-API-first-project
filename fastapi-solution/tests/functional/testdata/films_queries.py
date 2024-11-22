films_list_queries = [
    ({}, {"status": 200, "length": 50, "cashed_data": True}),
    # (
    #     {"sort": "imdb_rating"},
    #     {"status": 200, "length": 50, "cashed_data": True},
    # ),
    # (
    #     {"page_size": 30},
    #     {"status": 200, "length": 30, "cashed_data": True},
    # ),
    # ({"page_size": 0}, {"status": 422, "length": 1, "cashed_data": False}),
    # (
    #     {"page_number": 2},
    #     {"status": 200, "length": 50, "cashed_data": True},
    # ),
    # (
    #     {"page_number": 3},
    #     {"status": 200, "length": 20, "cashed_data": True},
    # ),
    # (
    #     {"page_number": 4},
    #     {"status": 404, "length": 1, "cashed_data": False},
    # ),
    # (
    #     {"genre": "6c162475-c7ed-4461-9184-001ef3d9f26e"},
    #     {"status": 200, "length": 50, "cashed_data": True},
    # ),
    # (
    #     {"genre": "6c162475-c7ed-4461-9184-001ef3d9none"},
    #     {"status": 404, "length": 1, "cashed_data": False},
    # ),
    # (
    #     {"genre": "Action"},
    #     {"status": 404, "length": 1, "cashed_data": False},
    # ),
    # (
    #     {
    #         "sort": "-imdb_rating",
    #         "page_size": 30,
    #         "page_number": 3,
    #         "genre": "6c162475-c7ed-4461-9184-001ef3d9f26e",
    #     },
    #     {"status": 200, "length": 30, "cashed_data": True},
    # ),
]

films_search_queries = [
    # (
    #     {"query": "The Star"},
    #     {"status": 200, "length": 50, "cashed_data": True},
    # ),
    # (
    #     {"query": "Mashed potato"},
    #     {"status": 404, "length": 1, "cashed_data": False},
    # ),
    # (
    #     {"query": "The Star", "page_size": 50, "page_number": 0},
    #     {"status": 404, "length": 1, "cashed_data": False},
    # ),
    # (
    #     {"query": "The Star", "page_size": 50, "page_number": 1},
    #     {"status": 200, "length": 50, "cashed_data": True},
    # ),
    # (
    #     {"query": "The Star", "page_size": 50, "page_number": 3},
    #     {"status": 200, "length": 20, "cashed_data": True},
    # ),
    # (
    #     {"query": "The Star", "page_size": 50, "page_number": 4},
    #     {"status": 404, "length": 1, "cashed_data": False},
    # ),
]
