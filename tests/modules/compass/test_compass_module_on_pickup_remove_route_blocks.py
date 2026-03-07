import unittest

from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.world import World
from modules.compass.compass_module import CompassModule
from tests.utils.metta import get_test_metta


class TestCompassModuleOnPickupRemoveRouteBlocks(unittest.TestCase):
    def test_pickup_compass_removes_route_blocks_from_glade(self):
        metta = get_test_metta()

        world = World()
        world.add_definition(RouteFactDefinition("glade", "north", "cave"))
        world.add_definition(RouteFactDefinition("glade", "south", "beach"))
        world.add_definition(RouteFactDefinition("cave", "east", "plane"))
        CompassModule(CharacterFactPattern("player", "John"), "glade").apply(world)
        metta.run(world.to_metta())

        # Add an extra block from a different location; it should remain.
        metta.run('(RouteBlock cave plane "Temporary blockade.")')

        pickup_trigger = TriggerFunctionPattern(PickUpEventPattern("compass", "glade"))
        metta.run(f"!{pickup_trigger.to_metta()}")

        glade_to_cave = RouteBlockFactPattern("glade", "cave", "$reason")
        result_glade_to_cave = metta.run(
            f"!(match &self {glade_to_cave.to_metta()} $reason)"
        )
        self.assertEqual(result_glade_to_cave, [[]])

        glade_to_beach = RouteBlockFactPattern("glade", "beach", "$reason")
        result_glade_to_beach = metta.run(
            f"!(match &self {glade_to_beach.to_metta()} $reason)"
        )
        self.assertEqual(result_glade_to_beach, [[]])

        cave_to_plane = RouteBlockFactPattern("cave", "plane", "$reason")
        result_cave_to_plane = metta.run(
            f"!(match &self {cave_to_plane.to_metta()} $reason)"
        )
        self.assertEqual(result_cave_to_plane[0][0], "Temporary blockade.")


if __name__ == "__main__":
    unittest.main()
