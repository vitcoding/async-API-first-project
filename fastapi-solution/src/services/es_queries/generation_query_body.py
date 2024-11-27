def generation_query_body(page_size, page_number, query):
    query_body = {
        "size": page_size,
        "from": (page_number - 1) * page_size,
    }

    if query is not None:
        query_body["query"] = {
            "multi_match": {
                "query": query,
                "fields": [
                    "title^3",
                    "description^2",
                    "genres",
                    "directors_names",
                    "actors_names",
                    "writers_names",
                ],
            }
        }
    return query_body
