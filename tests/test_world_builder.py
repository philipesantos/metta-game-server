import unittest

from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.functions.examine_function_pattern import ExamineFunctionPattern
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.functions.pickup_function_pattern import PickUpFunctionPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.functions.use_function_pattern import UseFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.world_builder import build_world
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output


class TestWorldBuilder(unittest.TestCase):
    def test_chest_items_are_defined_once(self):
        world = build_world()
        item_keys = [
            definition.key
            for definition in world.definitions
            if isinstance(definition, ItemFactDefinition)
        ]

        self.assertEqual(item_keys.count("shovel"), 1)
        self.assertEqual(item_keys.count("lantern"), 1)

    def test_look_in_chest_trigger_outputs_container_and_each_item_once(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        result = metta.run(
            f"!{TriggerFunctionPattern(LookInEventPattern('chest')).to_metta()}"
        )
        output_lines = format_metta_output(result).splitlines()

        self.assertEqual(output_lines.count("You look inside the chest."), 1)
        self.assertEqual(
            output_lines.count("Inside, an old shovel leans against the chest wall."),
            1,
        )
        self.assertEqual(
            output_lines.count("Inside, a weathered lantern lies in the chest."), 1
        )

    def test_look_in_well_lists_bucket_once(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        result = metta.run(
            f"!{TriggerFunctionPattern(LookInEventPattern('well')).to_metta()}"
        )
        output_lines = format_metta_output(result).splitlines()

        self.assertEqual(output_lines.count("You look inside the well."), 1)
        self.assertEqual(output_lines.count("A worn bucket hangs inside the well."), 1)

    def test_look_in_bucket_outputs_bucket_description(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        result = metta.run(
            f"!{TriggerFunctionPattern(LookInEventPattern('bucket')).to_metta()}"
        )
        output_lines = format_metta_output(result).splitlines()

        self.assertEqual(output_lines.count("You peer into the bucket."), 1)
        self.assertGreaterEqual(len(output_lines), 1)

    def test_satchel_can_be_picked_up(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        result = metta.run(f"!{PickUpFunctionPattern('satchel').to_metta()}")
        output_lines = format_metta_output(result).splitlines()
        self.assertIn("You pick up the satchel.", output_lines)

        satchel_state = StateWrapperPattern(AtFactPattern("satchel", "player"))
        satchel_state_result = metta.run(
            f"!(match &self {satchel_state.to_metta()} {satchel_state.to_metta()})"
        )
        self.assertEqual(
            unwrap_first_match(satchel_state_result), satchel_state.to_metta()
        )

    def test_look_in_beach_lists_waterfall_once(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        result = metta.run(
            f"!{TriggerFunctionPattern(LookInEventPattern('beach')).to_metta()}"
        )
        output_lines = format_metta_output(result).splitlines()

        self.assertEqual(
            output_lines.count(
                "A narrow waterfall spills down the rocks beside the beach."
            ),
            1,
        )

    def test_use_shovel_on_disturbed_soil_reveals_iron_box(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        metta.run(
            StateWrapperDefinition(AtFactPattern("player", "shore_path")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("shovel", "player")).to_metta())

        result = metta.run(
            f"!{UseFunctionPattern('shovel', 'disturbed_soil').to_metta()}"
        )
        output_lines = format_metta_output(result).splitlines()
        self.assertIn(
            "You dig into the disturbed soil and uncover a small iron box.",
            output_lines,
        )

        box_state = StateWrapperPattern(AtFactPattern("iron_box", "shore_path"))
        box_result = metta.run(
            f"!(match &self {box_state.to_metta()} {box_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(box_result), box_state.to_metta())

        soil_state = StateWrapperPattern(AtFactPattern("disturbed_soil", "shore_path"))
        soil_result = metta.run(
            f"!(match &self {soil_state.to_metta()} {soil_state.to_metta()})"
        )
        self.assertEqual(soil_result, [[]])

        shovel_state = StateWrapperPattern(AtFactPattern("shovel", "player"))
        shovel_result = metta.run(
            f"!(match &self {shovel_state.to_metta()} {shovel_state.to_metta()})"
        )
        self.assertEqual(shovel_result, [[]])

    def test_using_key_on_cabin_reveals_cabin_contents(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        locked_result = metta.run(
            f"!{TriggerFunctionPattern(LookInEventPattern('locked_cabin')).to_metta()}"
        )
        locked_output_lines = format_metta_output(locked_result).splitlines()
        self.assertIn("The cabin is locked.", locked_output_lines)
        self.assertNotIn("You peer inside the fireplace.", locked_output_lines)

        metta.run(
            StateWrapperDefinition(AtFactPattern("player", "hollow_path")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern("metal_key", "player")).to_metta()
        )
        unlock_result = metta.run(
            f"!{UseFunctionPattern('metal_key', 'locked_cabin').to_metta()}"
        )
        self.assertIn(
            "You unlock the cabin door.",
            format_metta_output(unlock_result).splitlines(),
        )
        metal_key_state = StateWrapperPattern(AtFactPattern("metal_key", "player"))
        metal_key_state_result = metta.run(
            f"!(match &self {metal_key_state.to_metta()} {metal_key_state.to_metta()})"
        )
        self.assertEqual(metal_key_state_result, [[]])
        locked_cabin_state = StateWrapperPattern(
            AtFactPattern("locked_cabin", "hollow_path")
        )
        locked_cabin_state_result = metta.run(
            f"!(match &self {locked_cabin_state.to_metta()} {locked_cabin_state.to_metta()})"
        )
        self.assertEqual(locked_cabin_state_result, [[]])
        cabin_state = StateWrapperPattern(AtFactPattern("cabin", "hollow_path"))
        cabin_state_result = metta.run(
            f"!(match &self {cabin_state.to_metta()} {cabin_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(cabin_state_result), cabin_state.to_metta())

        cabin_result = metta.run(
            f"!{TriggerFunctionPattern(LookInEventPattern('cabin')).to_metta()}"
        )
        cabin_output_lines = format_metta_output(cabin_result).splitlines()
        self.assertIn("You look inside the cabin.", cabin_output_lines)
        self.assertIn(
            "A cold stone fireplace is built into the far wall.", cabin_output_lines
        )
        self.assertIn(
            "One floorboard near the wall sits slightly loose.",
            cabin_output_lines,
        )

        fireplace_result = metta.run(
            f"!{TriggerFunctionPattern(LookInEventPattern('fireplace')).to_metta()}"
        )
        self.assertIn(
            "You peer inside the fireplace.",
            format_metta_output(fireplace_result).splitlines(),
        )

    def test_using_oil_on_lantern_creates_functioning_lantern(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        metta.run(StateWrapperDefinition(AtFactPattern("player", "glade")).to_metta())
        metta.run(StateWrapperDefinition(AtFactPattern("lantern", "player")).to_metta())
        metta.run(StateWrapperDefinition(AtFactPattern("oil", "player")).to_metta())

        result = metta.run(f"!{UseFunctionPattern('oil', 'lantern').to_metta()}")
        output_lines = format_metta_output(result).splitlines()

        self.assertIn(
            "You pour the oil into the lantern. It is ready to use.",
            output_lines,
        )

        oil_state = StateWrapperPattern(AtFactPattern("oil", "player"))
        oil_state_result = metta.run(
            f"!(match &self {oil_state.to_metta()} {oil_state.to_metta()})"
        )
        self.assertEqual(oil_state_result, [[]])

        lantern_state = StateWrapperPattern(AtFactPattern("lantern", "player"))
        lantern_state_result = metta.run(
            f"!(match &self {lantern_state.to_metta()} {lantern_state.to_metta()})"
        )
        self.assertEqual(lantern_state_result, [[]])

        functioning_lantern_state = StateWrapperPattern(
            AtFactPattern("functioning_lantern", "player")
        )
        functioning_lantern_state_result = metta.run(
            f"!(match &self {functioning_lantern_state.to_metta()} {functioning_lantern_state.to_metta()})"
        )
        self.assertEqual(
            unwrap_first_match(functioning_lantern_state_result),
            functioning_lantern_state.to_metta(),
        )

    def test_using_item_on_unhandled_target_shows_default_message(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        metta.run(StateWrapperDefinition(AtFactPattern("player", "glade")).to_metta())
        metta.run(StateWrapperDefinition(AtFactPattern("oil", "player")).to_metta())
        metta.run(StateWrapperDefinition(AtFactPattern("satchel", "player")).to_metta())

        result = metta.run(f"!{UseFunctionPattern('oil', 'satchel').to_metta()}")

        self.assertIn(
            "That doesn't seem to do anything.",
            format_metta_output(result).splitlines(),
        )


if __name__ == "__main__":
    unittest.main()
