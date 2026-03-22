from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResponseText:
    priority: int
    text: str
    raw: str


def parse_response_atom(atom_or_text: Any) -> ResponseText | None:
    if not isinstance(atom_or_text, str):
        return _parse_response_atom_obj(atom_or_text)
    return _parse_response_atom_text(atom_or_text)


def _parse_response_atom_obj(atom: Any) -> ResponseText | None:
    if not hasattr(atom, "get_children"):
        return None
    children = atom.get_children()
    if not children:
        return None
    if _atom_name(children[0]) != "Response":
        return None
    priority = _atom_to_int(children[1]) if len(children) > 1 else 0
    text_atom = children[2] if len(children) > 2 else None
    text = _render_text_atom(text_atom)
    raw = _atom_to_raw(text_atom)
    return ResponseText(priority=priority, text=text, raw=raw)


def _parse_response_atom_text(text: str) -> ResponseText | None:
    text = text.strip()
    if not text.startswith("(Response"):
        return None
    if not text.endswith(")"):
        return None
    body = text[1:-1].strip()
    if not body.startswith("Response"):
        return None
    rest = body[len("Response") :].strip()
    if not rest:
        return ResponseText(priority=0, text="", raw="")
    priority_token, text_expr = _split_first_token(rest)
    try:
        priority = int(priority_token)
    except ValueError:
        priority = 0
    text_expr = text_expr.strip()
    rendered = render_response_text(text_expr)
    return ResponseText(priority=priority, text=rendered, raw=text_expr)


def render_response_text(text_expr: str) -> str:
    if not text_expr:
        return ""
    if text_expr.startswith('"') and text_expr.endswith('"') and len(text_expr) >= 2:
        return text_expr[1:-1]
    return _format_text_atom(text_expr)


def _atom_name(atom: Any) -> str | None:
    if hasattr(atom, "get_name"):
        return atom.get_name()
    if hasattr(atom, "get_object"):
        obj = atom.get_object()
        if hasattr(obj, "value"):
            return str(obj.value)
        if hasattr(obj, "content"):
            return str(obj.content)
    return None


def _atom_to_int(atom: Any) -> int:
    if atom is None:
        return 0
    if hasattr(atom, "get_object"):
        obj = atom.get_object()
        if hasattr(obj, "value"):
            try:
                return int(obj.value)
            except (TypeError, ValueError):
                return 0
        if hasattr(obj, "content"):
            try:
                return int(obj.content)
            except (TypeError, ValueError):
                return 0
    if hasattr(atom, "get_name"):
        try:
            return int(atom.get_name())
        except (TypeError, ValueError):
            return 0
    try:
        return int(atom)
    except (TypeError, ValueError):
        return 0


def _atom_to_text(atom: Any) -> str:
    if atom is None:
        return ""
    if hasattr(atom, "get_object"):
        obj = atom.get_object()
        if hasattr(obj, "value"):
            return _format_text_atom(str(obj.value))
        if hasattr(obj, "content"):
            return _format_text_atom(str(obj.content))
    if hasattr(atom, "get_name"):
        return _format_text_atom(atom.get_name())
    if hasattr(atom, "get_children"):
        return _format_text_atom(str(atom))
    return _format_text_atom(str(atom))


def _render_text_atom(atom: Any) -> str:
    if atom is None:
        return ""
    if hasattr(atom, "get_children"):
        children = atom.get_children()
        if children:
            head = _atom_name(children[0])
            if head == "Text":
                parts = [_render_text_atom(child) for child in children[1:]]
                return "".join(part for part in parts if part)
            if head == "Cons":
                items = _collect_cons_list(atom)
                if items is not None:
                    return ", ".join(items)
    return _atom_to_text(atom)


def _collect_cons_list(atom: Any) -> list[str] | None:
    items: list[str] = []
    current = atom
    while True:
        if not hasattr(current, "get_children"):
            return None
        children = current.get_children()
        if not children:
            return None
        head = _atom_name(children[0])
        if head == "Nil":
            return items
        if head != "Cons" or len(children) < 3:
            return None
        items.append(_render_text_atom(children[1]))
        current = children[2]


def _atom_to_raw(atom: Any) -> str:
    if atom is None:
        return ""
    if hasattr(atom, "get_object"):
        obj = atom.get_object()
        if hasattr(obj, "value"):
            return str(obj.value)
        if hasattr(obj, "content"):
            return str(obj.content)
    if hasattr(atom, "get_name"):
        return atom.get_name()
    return str(atom)


def _strip_single_parens(text: str) -> str:
    if not text:
        return text
    trimmed = text.strip()
    if trimmed.startswith("(") and trimmed.endswith(")"):
        inner = trimmed[1:-1].strip()
        if inner and " " not in inner and "(" not in inner and ")" not in inner:
            return inner
    return text


def _format_text_atom(text: str) -> str:
    stripped = _strip_single_parens(text)
    if stripped is not text:
        return stripped
    trimmed = text.strip()
    if trimmed.startswith("(") and trimmed.endswith(")"):
        inner = trimmed[1:-1].strip()
        if inner and " " in inner and "(" not in inner and ")" not in inner:
            return ", ".join(inner.split())
    return text


def _split_first_token(text: str) -> tuple[str, str]:
    index = 0
    length = len(text)
    while index < length and text[index].isspace():
        index += 1
    start = index
    while index < length and not text[index].isspace() and text[index] != ")":
        index += 1
    return text[start:index], text[index:].strip()


def _is_empty_metta_output(output: Any) -> bool:
    if output is None:
        return True
    if isinstance(output, str):
        return output.strip() in {"", "[]", "[[]]"}
    if isinstance(output, list):
        return not output or all(_is_empty_metta_output(item) for item in output)
    return False


def _is_empty_raw_value(raw: str) -> bool:
    return raw in {"", "[]", "[[]]", "Empty", "(Empty)", "()", "{}"}


def collect_raw_metta_output(output: Any) -> tuple[str, ...]:
    if _is_empty_metta_output(output):
        return ()

    if isinstance(output, str):
        atoms = _find_response_atoms(output)
        if atoms:
            return tuple(atom for atom in atoms if atom.strip())
        stripped = output.strip()
        return (stripped,) if not _is_empty_raw_value(stripped) else ()

    raw_values: list[str] = []
    for atom in _iter_metta_atoms(output):
        raw = str(atom).strip()
        if not _is_empty_raw_value(raw):
            raw_values.append(raw)
    return tuple(raw_values)


def format_metta_output(output: Any) -> str:
    if _is_empty_metta_output(output):
        return ""

    if isinstance(output, str):
        atoms = _find_response_atoms(output)
        if not atoms:
            return output
        responses: list[ResponseText] = []
        for atom in atoms:
            response = parse_response_atom(atom)
            if response and response.text:
                responses.append(response)
        responses.sort(key=lambda item: (-item.priority, item.text))
        return "\n".join(item.text for item in responses)

    responses: list[ResponseText] = []
    for atom in _iter_metta_atoms(output):
        response = parse_response_atom(atom)
        if response is None:
            response = parse_response_atom(str(atom))
        if response and response.text:
            responses.append(response)
    if not responses:
        fallback_from_string = format_metta_output(str(output))
        if fallback_from_string != str(output):
            return fallback_from_string
        return str(output)
    responses.sort(key=lambda item: (-item.priority, item.text))
    return "\n".join(item.text for item in responses)


def _find_response_atoms(output: str) -> list[str]:
    atoms = []
    index = 0
    length = len(output)
    in_string = False
    escape = False

    while index < length:
        char = output[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            index += 1
            continue

        if output.startswith("(Response", index):
            atom, next_index = _extract_sexpr(output, index)
            if atom:
                atoms.append(atom)
                index = next_index
                continue

        index += 1

    return atoms


def _extract_sexpr(text: str, start_index: int) -> tuple[str | None, int]:
    depth = 0
    index = start_index
    length = len(text)
    in_string = False
    escape = False

    while index < length:
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            index += 1
            continue

        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start_index : index + 1], index + 1

        index += 1

    return None, start_index


def _iter_metta_atoms(output: Any):
    if isinstance(output, list):
        for item in output:
            yield from _iter_metta_atoms(item)
        return

    if hasattr(output, "get_children"):
        children = output.get_children()
        if not children:
            yield output
            return
        if children and _atom_name(children[0]) == "Response":
            yield output
            return
        for child in children:
            yield from _iter_metta_atoms(child)
        return

    yield output
