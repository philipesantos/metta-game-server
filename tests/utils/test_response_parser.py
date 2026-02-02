import unittest

from utils.response import parse_response_atom, ResponseText


class _FakeObj:
    def __init__(self, value=None, content=None):
        self.value = value
        self.content = content


class _FakeAtom:
    def __init__(self, name=None, obj=None, children=None):
        self._name = name
        self._obj = obj
        self._children = children or []

    def get_name(self):
        return self._name

    def get_object(self):
        return self._obj

    def get_children(self):
        return self._children


class TestResponseParser(unittest.TestCase):
    def test_parse_response_atom_from_string(self):
        response = parse_response_atom('(Response 42 "Hello")')
        self.assertEqual(response, ResponseText(priority=42, text="Hello", raw='"Hello"'))

    def test_parse_response_atom_from_children(self):
        response_atom = _FakeAtom(
            children=[
                _FakeAtom(name="Response"),
                _FakeAtom(obj=_FakeObj(value=7)),
                _FakeAtom(obj=_FakeObj(value="Hi there")),
            ]
        )
        response = parse_response_atom(response_atom)
        self.assertEqual(response, ResponseText(priority=7, text="Hi there", raw="Hi there"))


if __name__ == "__main__":
    unittest.main()
