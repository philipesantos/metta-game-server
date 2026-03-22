import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.world import World
from modules.compass.compass_module import CompassModule
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output


class TestCompassModule(unittest.TestCase):
    def test_adds_satchel_in_glade_with_compass_inside(self):
        world = World()

        CompassModule(
            CharacterFactPattern("player", "John"),
            LocationFactDefinition("glade", "A quiet glade."),
        ).apply(world)

        satchels = [
            definition
            for definition in world.definitions
            if isinstance(definition, ContainerFactDefinition)
            and definition.key == "satchel"
        ]
        self.assertEqual(len(satchels), 1)

        compasses = [
            definition
            for definition in world.definitions
            if isinstance(definition, ItemFactDefinition)
            and definition.key == "compass"
        ]
        self.assertEqual(len(compasses), 1)

        satchel_state_defs = [
            definition
            for definition in world.definitions
            if isinstance(definition, StateWrapperDefinition)
            and isinstance(definition.pattern, AtFactPattern)
            and definition.pattern.what == "satchel"
            and definition.pattern.where == "glade"
        ]
        self.assertEqual(len(satchel_state_defs), 1)

        compass_state_defs = [
            definition
            for definition in world.definitions
            if isinstance(definition, StateWrapperDefinition)
            and isinstance(definition.pattern, AtFactPattern)
            and definition.pattern.what == "compass"
            and definition.pattern.where == "satchel"
        ]
        self.assertEqual(len(compass_state_defs), 1)

    def test_adds_route_blocks_from_compass_location(self):
        metta = get_test_metta()

        world = World()
        world.add_definition(RouteFactDefinition("glade", "north", "cave"))
        world.add_definition(RouteFactDefinition("glade", "south", "beach"))
        world.add_definition(RouteFactDefinition("cave", "east", "plane"))

        CompassModule(
            CharacterFactPattern("player", "John"),
            LocationFactDefinition("glade", "A quiet glade."),
        ).apply(world)
        metta.run(world.to_metta())

        glade_to_cave = RouteBlockFactPattern("glade", "cave", "$reason")
        result_glade_to_cave = metta.run(
            f"!(match &self {glade_to_cave.to_metta()} $reason)"
        )
        self.assertEqual(
            unwrap_first_match(result_glade_to_cave),
            "You hesitate. This isn’t a place to wander blindly.",
        )

        glade_to_beach = RouteBlockFactPattern("glade", "beach", "$reason")
        result_glade_to_beach = metta.run(
            f"!(match &self {glade_to_beach.to_metta()} $reason)"
        )
        self.assertEqual(
            unwrap_first_match(result_glade_to_beach),
            "You hesitate. This isn’t a place to wander blindly.",
        )

        cave_to_plane = RouteBlockFactPattern("cave", "plane", "$reason")
        result_cave_to_plane = metta.run(
            f"!(match &self {cave_to_plane.to_metta()} {cave_to_plane.to_metta()})"
        )
        self.assertEqual(result_cave_to_plane, [[]])

    def test_pickup_compass_prints_directions_after_unblocking_routes(self):
        metta = get_test_metta()

        world = World()
        world.add_definition(RouteFactDefinition("glade", "north", "cave"))
        world.add_definition(
            RouteFactDefinition(
                "glade",
                "south",
                "beach",
                "To the south, a sandy path leads toward the beach.",
            )
        )
        world.add_definition(
            StateWrapperDefinition(AtFactPattern("player", "glade"))
        )

        CompassModule(
            CharacterFactPattern("player", "John"),
            LocationFactDefinition("glade", "A quiet glade."),
        ).apply(world)
        metta.run(world.to_metta())

        pickup_trigger = TriggerFunctionPattern(PickUpEventPattern("compass", "satchel"))
        result = metta.run(f"!{pickup_trigger.to_metta()}")
        output_lines = format_metta_output(result).splitlines()

        self.assertIn(
            "To the south, a sandy path leads toward the beach.",
            output_lines,
        )


if __name__ == "__main__":
    unittest.main()
