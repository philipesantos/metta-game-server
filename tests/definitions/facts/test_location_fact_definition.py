import unittest

from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta

from core.patterns.facts.location_fact_pattern import LocationFactPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from tests.utils.utils import unwrap_first_match
from utils.type import Type


class TestLocationFactDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        key = "glade"
        description = "The glade description"

        metta.run(LocationFactDefinition(key, description).to_metta())

        result_type = metta.run(f"!(get-type {key})")
        self.assertEqual(unwrap_first_match(result_type), Type.LOCATION.value)

        location_key = LocationFactPattern("$key")
        result_key = metta.run(f"!(match &self {location_key.to_metta()} $key)")
        self.assertEqual(unwrap_first_match(result_key), key)

        location_move_trigger = TriggerFunctionPattern(MoveEventPattern("cave", key))
        result_move_trigger = metta.run(f"!{location_move_trigger.to_metta()}")
        self.assertEqual(unwrap_first_match(result_move_trigger).text, description)

        location_no_match = LocationFactPattern("cave")
        result_no_match = metta.run(
            f"!(match &self {location_no_match.to_metta()} True)"
        )
        self.assertEqual(result_no_match, [[]])


if __name__ == "__main__":
    unittest.main()
