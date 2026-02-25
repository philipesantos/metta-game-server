import unittest

from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.patterns.events.drop_event_pattern import DropEventPattern
from core.patterns.events.examine_event_pattern import ExamineEventPattern
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.item_fact_pattern import ItemFactPattern
from core.patterns.facts.location_fact_pattern import LocationFactPattern
from core.patterns.facts.pickupable_fact_pattern import PickupableFactPattern
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
        text_examine = "The compass needle points north."
        name = "Old compass"
        text_enter = "An old compass lies on a mossy stone."
        text_look = "Inside, an old compass rests against the lining."

        metta.run(
            ItemFactDefinition(
                key,
                text_pickup,
                text_drop,
                text_examine,
                name=name,
                text_enter=text_enter,
                text_look=text_look,
            ).to_metta()
        )

        result_type = metta.run(f"!(get-type {key})")
        self.assertEqual(unwrap_first_match(result_type), Type.ITEM.value)

        item_key = ItemFactPattern("$key")
        result_key = metta.run(f"!(match &self {item_key.to_metta()} $key)")
        self.assertEqual(unwrap_first_match(result_key), key)

        pickupable_item = PickupableFactPattern("$key")
        result_pickupable = metta.run(f"!(match &self {pickupable_item.to_metta()} $key)")
        self.assertEqual(unwrap_first_match(result_pickupable), key)

        item_pickup_trigger = TriggerFunctionPattern(PickUpEventPattern(key, "glade"))
        result_pickup_trigger = metta.run(f"!{item_pickup_trigger.to_metta()}")
        self.assertEqual(unwrap_first_match(result_pickup_trigger).text, text_pickup)

        item_drop_trigger = TriggerFunctionPattern(DropEventPattern(key, "glade"))
        result_drop_trigger = metta.run(f"!{item_drop_trigger.to_metta()}")
        self.assertEqual(unwrap_first_match(result_drop_trigger).text, text_drop)

        item_examine_trigger = TriggerFunctionPattern(ExamineEventPattern(key))
        result_examine_trigger = metta.run(f"!{item_examine_trigger.to_metta()}")
        self.assertEqual(unwrap_first_match(result_examine_trigger).text, text_examine)

        result_enter_text = metta.run(f"!(match &self (ItemEnterText {key} $text) $text)")
        self.assertEqual(unwrap_first_match(result_enter_text), text_enter)

        result_look_text = metta.run(f"!(match &self (ItemLookText {key} $text) $text)")
        self.assertEqual(unwrap_first_match(result_look_text), text_look)

        result_name = metta.run(f"!(match &self (ItemName {key} $name) $name)")
        self.assertEqual(unwrap_first_match(result_name), name)

        item_no_match = LocationFactPattern("bottle")
        result_no_match = metta.run(f"!(match &self {item_no_match.to_metta()} True)")
        self.assertEqual(result_no_match, [[]])

    def test_to_metta_non_pickupable_item(self):
        metta = get_test_metta()

        key = "cave_door"
        metta.run(ItemFactDefinition(key, "", "", "A carved door.", can_pickup=False).to_metta())

        pickupable_item = PickupableFactPattern("$key")
        result_pickupable = metta.run(f"!(match &self {pickupable_item.to_metta()} $key)")
        self.assertEqual(result_pickupable, [[]])


if __name__ == "__main__":
    unittest.main()
