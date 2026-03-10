import unittest

from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern
from core.world import World
from modules.compass.compass_module import CompassModule
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match


class TestCompassModule(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
