def split_expressions(metta: str) -> list[str]:
    expressions: list[str] = []
    current: list[str] = []
    depth = 0
    in_string = False
    escaped = False

    for char in metta:
        if depth == 0 and char.isspace():
            continue

        current.append(char)

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                expressions.append("".join(current).strip())
                current = []

    return expressions
