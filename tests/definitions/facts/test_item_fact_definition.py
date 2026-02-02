import unittest

from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.patterns.events.drop_event_pattern import DropEventPattern
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.item_fact_pattern import ItemFactPattern
from core.patterns.facts.location_fact_pattern import LocationFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.type import Type


class TestItemFactDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        key = "compass"
        text_pickup = "You pick up the compass."
        text_drop = "You drop the compass."

        metta.run(ItemFactDefinition(key, text_pickup, text_drop).to_metta())

        result_type = metta.run(f"!(get-type {key})")
        self.assertEqual(unwrap_first_match(result_type), Type.ITEM.value)

        item_key = ItemFactPattern("$key")
        result_key = metta.run(f"!(match &self {item_key.to_metta()} $key)")
        self.assertEqual(unwrap_first_match(result_key), key)

        item_pickup_trigger = TriggerFunctionPattern(PickUpEventPattern(key, "glade"))
        result_pickup_trigger = metta.run(f"!{item_pickup_trigger.to_metta()}")
        self.assertEqual(unwrap_first_match(result_pickup_trigger).text, text_pickup)

        item_drop_trigger = TriggerFunctionPattern(DropEventPattern(key, "glade"))
        result_drop_trigger = metta.run(f"!{item_drop_trigger.to_metta()}")
        self.assertEqual(unwrap_first_match(result_drop_trigger).text, text_drop)

        item_no_match = LocationFactPattern("bottle")
        result_no_match = metta.run(f"!(match &self {item_no_match.to_metta()} True)")
        self.assertEqual(result_no_match, [[]])


if __name__ == "__main__":
    unittest.main()
