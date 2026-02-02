from utils.response import ResponseText, parse_response_atom


def unwrap_atom(atom):
    if hasattr(atom, "get_object"):
        obj = atom.get_object()
        if hasattr(obj, "value"):
            return obj.value
        if hasattr(obj, "content"):
            return obj.content
        return obj
    if hasattr(atom, "get_name"):
        return atom.get_name()
    if hasattr(atom, "get_children"):
        text = str(atom)
        response = parse_response_atom(text)
        return response if response is not None else text
    return atom


def unwrap_first_match(result):
    return unwrap_match(result, 0)


def unwrap_match(result, index):
    if not result:
        raise AssertionError("Expected match results, got empty list")
    if not result[0]:
        raise AssertionError("Expected first match to have bindings")
    return unwrap_atom(result[0][index])


def count_atoms(result):
    if not result:
        raise AssertionError("Expected match results, got empty list")
    return len(result[0])
