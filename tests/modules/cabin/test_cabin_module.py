import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.world import World
from modules.cabin.cabin_module import CabinModule


class TestCabinModule(unittest.TestCase):
    def test_adds_locked_cabin_definition_and_unlock_trigger(self):
        world = World()
        hollow_path = LocationFactDefinition(
            "hollow_path", "You are on a quiet path through a shallow hollow."
        )
        seashell = ContainerFactDefinition(
            "seashell",
            text_contents="A seashell rests here.",
        )
        oil = ItemFactDefinition("oil", "pick", "drop", "examine")

        CabinModule(hollow_path, seashell, [oil]).apply(world)

        metal_keys = [
            definition
            for definition in world.definitions
            if isinstance(definition, ItemFactDefinition)
            and definition.key == "metal_key"
        ]
        self.assertEqual(len(metal_keys), 1)
        cabin_containers = [
            definition
            for definition in world.definitions
            if isinstance(definition, ContainerFactDefinition)
            and definition.key in ("locked_cabin", "cabin", "fireplace", "loose_board")
        ]
        self.assertEqual(len(cabin_containers), 4)
        cabin_state_defs = [
            definition
            for definition in world.definitions
            if isinstance(definition, StateWrapperDefinition)
            and isinstance(definition.pattern, AtFactPattern)
            and definition.pattern.what == "locked_cabin"
            and definition.pattern.where == "hollow_path"
        ]
        self.assertEqual(len(cabin_state_defs), 1)
        key_state_defs = [
            definition
            for definition in world.definitions
            if isinstance(definition, StateWrapperDefinition)
            and isinstance(definition.pattern, AtFactPattern)
            and definition.pattern.what == "metal_key"
            and definition.pattern.where == "seashell"
        ]
        self.assertEqual(len(key_state_defs), 1)
        fireplace_state_defs = [
            definition
            for definition in world.definitions
            if isinstance(definition, StateWrapperDefinition)
            and isinstance(definition.pattern, AtFactPattern)
            and definition.pattern.what == "fireplace"
            and definition.pattern.where == "cabin"
        ]
        self.assertEqual(len(fireplace_state_defs), 1)
        loose_board_state_defs = [
            definition
            for definition in world.definitions
            if isinstance(definition, StateWrapperDefinition)
            and isinstance(definition.pattern, AtFactPattern)
            and definition.pattern.what == "loose_board"
            and definition.pattern.where == "cabin"
        ]
        self.assertEqual(len(loose_board_state_defs), 1)
        oil_state_defs = [
            definition
            for definition in world.definitions
            if isinstance(definition, StateWrapperDefinition)
            and isinstance(definition.pattern, AtFactPattern)
            and definition.pattern.what == "oil"
            and definition.pattern.where == "fireplace"
        ]
        self.assertEqual(len(oil_state_defs), 1)
        unlock_triggers = [
            definition
            for definition in world.definitions
            if isinstance(definition, TriggerFunctionDefinition)
            and isinstance(definition.event, UseEventPattern)
            and definition.event.what == "metal_key"
            and definition.event.with_what == "locked_cabin"
        ]
        self.assertEqual(len(unlock_triggers), 1)


if __name__ == "__main__":
    unittest.main()
