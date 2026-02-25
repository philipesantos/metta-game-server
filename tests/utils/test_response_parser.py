import unittest

from utils.response import format_metta_output, parse_response_atom, ResponseText


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


class _StringOnlyResponseAtom:
    def get_children(self):
        return []

    def __str__(self):
        return '(Response 60 "You can go: north, east")'


class TestResponseParser(unittest.TestCase):
    def test_parse_response_atom_from_string(self):
        response = parse_response_atom('(Response 42 "Hello")')
        self.assertEqual(
            response, ResponseText(priority=42, text="Hello", raw='"Hello"')
        )

    def test_parse_response_atom_from_children(self):
        response_atom = _FakeAtom(
            children=[
                _FakeAtom(name="Response"),
                _FakeAtom(obj=_FakeObj(value=7)),
                _FakeAtom(obj=_FakeObj(value="Hi there")),
            ]
        )
        response = parse_response_atom(response_atom)
        self.assertEqual(
            response, ResponseText(priority=7, text="Hi there", raw="Hi there")
        )

    def test_format_metta_output_collects_nested_response_atoms(self):
        nested = [
            [
                _FakeAtom(
                    children=[
                        _FakeAtom(name="Wrapper"),
                        _FakeAtom(
                            children=[
                                _FakeAtom(name="Response"),
                                _FakeAtom(obj=_FakeObj(value=20)),
                                _FakeAtom(obj=_FakeObj(value="Visible line")),
                            ]
                        ),
                    ]
                )
            ]
        ]

        self.assertEqual(format_metta_output(nested), "Visible line")

    def test_format_metta_output_falls_back_to_string_parsing_for_atoms(self):
        output = [[_StringOnlyResponseAtom()]]
        self.assertEqual(format_metta_output(output), "You can go: north, east")


if __name__ == "__main__":
    unittest.main()
