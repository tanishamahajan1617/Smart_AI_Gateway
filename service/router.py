def select_best_key(keys, required_tokens, query_type):
    valid_keys = []

    for k in keys:
        remaining = k["limit"] - k["used_tokens"]
        priority = k.get("priority", 3)

        if remaining >= required_tokens:
            valid_keys.append({
                "key": k,
                "remaining": remaining,
                "priority": priority
            })

    if not valid_keys:
        return None

    valid_keys.sort(
        key=lambda x: (
            x["priority"],
            -x["remaining"]
        )
    )

    return valid_keys[0]["key"]