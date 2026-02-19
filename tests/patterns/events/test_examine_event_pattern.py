import unittest

from core.patterns.events.examine_event_pattern import ExamineEventPattern


class TestExamineEventPattern(unittest.TestCase):
    def test_to_metta(self):
        examine_event = ExamineEventPattern("compass")
        self.assertEqual(examine_event.to_metta(), "(Examine compass)")


if __name__ == "__main__":
    unittest.main()
