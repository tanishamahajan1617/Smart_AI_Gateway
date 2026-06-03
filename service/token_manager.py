def estimate_tokens(text: str):
    return max(1, len(text) // 4)