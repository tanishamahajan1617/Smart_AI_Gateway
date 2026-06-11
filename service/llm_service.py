def call_llm(provider: str, api_key: str, query: str):
    #Replace with real API later

    response_text = f"Response from {provider}: {query}"

    tokens_used = len(query.split()) * 2

    return response_text, tokens_used