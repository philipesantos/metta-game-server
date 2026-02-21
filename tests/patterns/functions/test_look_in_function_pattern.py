import unittest

from core.patterns.functions.look_in_function_pattern import LookInFunctionPattern


class TestLookInFunctionPattern(unittest.TestCase):
    def test_to_metta(self):
        action = LookInFunctionPattern("chest")
        self.assertEqual(action.to_metta(), "(look-in (chest))")


if __name__ == "__main__":
    unittest.main()
