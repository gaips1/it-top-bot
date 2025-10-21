def split_text(text: str, limit: int = 4096) -> list[str]:
    if len(text) <= limit:
        return [text]

    parts = []
    remaining_text = text

    while remaining_text:
        if len(remaining_text) <= limit:
            parts.append(remaining_text)
            break

        chunk = remaining_text[:limit]
        
        last_newline = chunk.rfind('\n')
        last_space = chunk.rfind(' ')

        split_pos = max(last_newline, last_space)

        if split_pos == -1:
            split_pos = limit
        
        parts.append(remaining_text[:split_pos])
        
        remaining_text = remaining_text[split_pos:].lstrip()

    return parts