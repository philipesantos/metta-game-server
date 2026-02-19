import unittest

from core.patterns.functions.examine_function_pattern import ExamineFunctionPattern


class TestExamineFunctionPattern(unittest.TestCase):
    def test_to_metta(self):
        examine_function = ExamineFunctionPattern("compass")
        self.assertEqual(examine_function.to_metta(), "(examine (compass))")


if __name__ == "__main__":
    unittest.main()
