def classify_query(query: str, file_type: str = None):
    query = query.lower()

    #  Detect complexity
    if len(query.split()) < 5:
        complexity = "simple"
    else:
        complexity = "complex"

    # Detect intent
    if "explain" in query:
        intent = "explain"
    elif "summarize" in query:
        intent = "summarize"
    elif "analyze" in query:
        intent = "analyze"
    else:
        intent = "general"

    #  Detect modality
    if file_type:
        if "image" in file_type:
            modality = "image"
        elif "pdf" in file_type:
            modality = "document"
        else:
            modality = "file"
    else:
        modality = "text"

    return {
        "complexity": complexity,
        "intent": intent,
        "modality": modality
    }