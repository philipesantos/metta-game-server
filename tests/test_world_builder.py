import unittest

from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.functions.move_towards_function_pattern import (
    MoveTowardsFunctionPattern,
)
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.functions.use_function_pattern import UseFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.world_builder import build_world
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.direction import Direction
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
            output_lines.count("Inside, a weathered lantern lies in the chest."),
            1,
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

        self.assertEqual(output_lines.count("A worn bucket hangs inside the well."), 1)
        self.assertGreaterEqual(len(output_lines), 1)

    def test_use_shovel_on_disturbed_soil_reveals_iron_box(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        metta.run(StateWrapperDefinition(AtFactPattern("player", "path_2")).to_metta())
        metta.run(StateWrapperDefinition(AtFactPattern("shovel", "player")).to_metta())

        result = metta.run(
            f"!{UseFunctionPattern('shovel', 'disturbed_soil').to_metta()}"
        )
        output_lines = format_metta_output(result).splitlines()
        self.assertIn(
            "You dig into the disturbed soil and uncover a small iron box.",
            output_lines,
        )

        box_state = StateWrapperPattern(AtFactPattern("iron_box", "path_2"))
        box_result = metta.run(
            f"!(match &self {box_state.to_metta()} {box_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(box_result), box_state.to_metta())

        soil_state = StateWrapperPattern(AtFactPattern("disturbed_soil", "path_2"))
        soil_result = metta.run(
            f"!(match &self {soil_state.to_metta()} {soil_state.to_metta()})"
        )
        self.assertEqual(soil_result, [[]])

    def test_using_metal_key_on_cabin_unlocks_path_to_cabin(self):
        metta = get_test_metta()
        metta.run(build_world().to_metta())

        metta.run(StateWrapperDefinition(AtFactPattern("player", "path_5")).to_metta())
        blocked_result = metta.run(
            f"!{MoveTowardsFunctionPattern(Direction.WEST).to_metta()}"
        )
        self.assertEqual(
            unwrap_first_match(blocked_result).text,
            "The cabin is locked. You need a key.",
        )

        metta.run(
            StateWrapperDefinition(AtFactPattern("metal_key", "player")).to_metta()
        )
        metta.run(f"!{UseFunctionPattern('metal_key', 'cabin').to_metta()}")

        metta.run(StateWrapperDefinition(AtFactPattern("player", "path_5")).to_metta())
        unlocked_result = metta.run(
            f"!{MoveTowardsFunctionPattern(Direction.WEST).to_metta()}"
        )
        output_lines = format_metta_output(unlocked_result).splitlines()
        self.assertIn("You are in the cabin.", output_lines)


if __name__ == "__main__":
    unittest.main()
