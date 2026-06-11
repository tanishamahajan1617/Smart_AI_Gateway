def select_best_key(keys, classification):
    has_priority = any(k.priority is not None for k in keys)

    modality = classification["modality"]
    complexity = classification["complexity"]

    # Step 1: Filter by modality (future-ready)
    if modality == "image":
        keys = [k for k in keys if "vision" in k.provider.lower() or "gpt" in k.provider.lower()]

    elif modality == "document":
        # you can later prefer doc-capable models
        pass

    # Step 2: Apply routing strategy

    if has_priority:
        #  USER-CONTROLLED MODE
        sorted_keys = sorted(
            keys,
            key=lambda k: (
                -(k.priority or 0),
                k.used_tokens
            )
        )

    else:
        #  SYSTEM-CONTROLLED MODE

        if complexity == "simple":
            # cheap first
            sorted_keys = sorted(keys, key=lambda k: k.used_tokens)
        else:
            # strong first (fallback to priority if exists)
            sorted_keys = sorted(
                keys,
                key=lambda k: (-(k.priority or 0), k.used_tokens)
            )

    return sorted_keys[0] if sorted_keys else None