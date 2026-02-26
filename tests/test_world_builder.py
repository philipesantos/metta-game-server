import unittest

from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.world_builder import build_world
from tests.utils.metta import get_test_metta
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


if __name__ == "__main__":
    unittest.main()
