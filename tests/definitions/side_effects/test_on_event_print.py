import unittest

from core.definitions.side_effects.on_event_print import OnEventPrint
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta

from core.patterns.events.move_event_pattern import MoveEventPattern
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from tests.utils.utils import unwrap_first_match


class TestOnEventPrint(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        text = "Location description"
        side_effect = OnEventPrint(text)

        trigger = TriggerFunctionDefinition(
            MoveEventPattern("$from", "glade"), [side_effect]
        )
        metta.run(trigger.to_metta())

        trigger_metta_usage = TriggerFunctionPattern(MoveEventPattern("cave", "glade"))
        result = metta.run(f"!{trigger_metta_usage.to_metta()}")
        self.assertEqual(unwrap_first_match(result).text, text)


if __name__ == "__main__":
    unittest.main()
