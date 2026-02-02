import unittest

from core.definitions.side_effects.on_event_print import OnEventPrint
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta

from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from tests.utils.some_event import SomeEventPattern
from tests.utils.utils import unwrap_first_match


class TestTriggerFunctionDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        side_effect_text = "Trigger text"
        event = SomeEventPattern("$value")
        side_effect = OnEventPrint(side_effect_text)

        metta.run(TriggerFunctionDefinition(event, [side_effect]).to_metta())

        trigger = TriggerFunctionPattern(SomeEventPattern("glade"))
        result = metta.run(f"!{trigger.to_metta()}")
        self.assertEqual(unwrap_first_match(result).text, side_effect_text)


if __name__ == "__main__":
    unittest.main()
