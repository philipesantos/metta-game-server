import unittest

from core.patterns.events.look_in_event_pattern import LookInEventPattern


class TestLookInEventPattern(unittest.TestCase):
    def test_to_metta(self):
        event = LookInEventPattern("chest")
        self.assertEqual(event.to_metta(), "(LookIn chest)")


if __name__ == "__main__":
    unittest.main()
