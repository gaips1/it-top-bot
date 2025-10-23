def split_text(text: str, limit: int = 4096) -> list[str]:
    parts = []
    current_part = ""
    lines = text.split('\n')

    for line in lines:
        if len(current_part) + len(line) + 1 > limit:
            parts.append(current_part)
            current_part = line
        else:
            if current_part:
                current_part += "\n"
            current_part += line
    if current_part:
        parts.append(current_part)

    return parts