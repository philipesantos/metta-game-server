import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.world import World
from modules.cabin.cabin_module import CabinModule
from modules.cabin.side_effects.cabin_module_on_use_unlock import CabinModuleOnUseUnlock


class TestCabinModule(unittest.TestCase):
    def test_adds_locked_route_and_unlock_trigger(self):
        world = World()
        path_5 = LocationFactDefinition("path_5", "Path 5")
        cabin = LocationFactDefinition("cabin", "Cabin")
        seashell = ContainerFactDefinition("seashell")
        oil = ItemFactDefinition("oil", "pick", "drop", "examine")

        CabinModule(path_5, cabin, seashell, [oil]).apply(world)

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
            and definition.key in ("fireplace", "loose_board")
        ]
        self.assertEqual(len(cabin_containers), 2)

        route_blocks = [
            definition
            for definition in world.definitions
            if isinstance(definition, RouteBlockFactDefinition)
        ]
        self.assertEqual(len(route_blocks), 1)
        self.assertEqual(route_blocks[0].location_from, "path_5")
        self.assertEqual(route_blocks[0].location_to, "cabin")
        self.assertEqual(route_blocks[0].reason, "The cabin is locked. You need a key.")

        cabin_state_defs = [
            definition
            for definition in world.definitions
            if isinstance(definition, StateWrapperDefinition)
            and isinstance(definition.pattern, AtFactPattern)
            and definition.pattern.what == "cabin"
            and definition.pattern.where == "path_5"
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
            and definition.event.with_what == "cabin"
        ]
        self.assertEqual(len(unlock_triggers), 1)
        self.assertTrue(
            any(
                isinstance(side_effect, CabinModuleOnUseUnlock)
                for side_effect in unlock_triggers[0].side_effects
            )
        )


if __name__ == "__main__":
    unittest.main()
