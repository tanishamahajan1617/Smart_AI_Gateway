def classify_query(query: str):
    length = len(query)

    if length < 50:
        return "simple"
    elif length < 200:
        return "medium"
    else:
        return "complex"