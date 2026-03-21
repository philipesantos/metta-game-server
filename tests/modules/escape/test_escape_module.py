import unittest
from unittest.mock import patch

from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.use_function_definition import UseFunctionDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.world import World
from modules.escape.escape_module import EscapeModule
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output


class TestEscapeModule(unittest.TestCase):
    @patch(
        "modules.escape.escape_module.random.choice", side_effect=lambda items: items[0]
    )
    def test_using_propeller_on_boat_wins_when_propeller_is_chosen(self, _choice):
        metta = get_test_metta()

        world = World()
        character = CharacterFactPattern("player", "John")
        beach = LocationFactDefinition("beach", "A broad beach.")
        plane_site = LocationFactDefinition("plane_site", "A wreck site in the trees.")

        world.add_definition(ExistsFunctionDefinition())
        world.add_definition(UseFunctionDefinition(character))
        world.add_definition(beach)
        world.add_definition(plane_site)

        escape_module = EscapeModule(beach, plane_site)
        escape_module.apply(world)

        world.add_definition(StateWrapperDefinition(AtFactPattern("player", "beach")))
        world.add_definition(
            StateWrapperDefinition(AtFactPattern("propeller", "player"))
        )
        metta.run(world.to_metta())

        result = metta.run("!(use (propeller boat))")

        self.assertIn(
            "You fit the propeller onto the boat's motor. The engine catches, and you steer out across the water toward freedom.",
            format_metta_output(result),
        )

        game_won_result = metta.run("!(match &self (State (GameWon $reason)) $reason)")
        self.assertEqual(
            unwrap_first_match(game_won_result),
            "You fit the propeller onto the boat's motor. The engine catches, and you steer out across the water toward freedom.",
        )

    @patch(
        "modules.escape.escape_module.random.choice", side_effect=lambda items: items[1]
    )
    def test_using_battery_on_plane_wins_when_battery_is_chosen(self, _choice):
        metta = get_test_metta()

        world = World()
        character = CharacterFactPattern("player", "John")
        beach = LocationFactDefinition("beach", "A broad beach.")
        plane_site = LocationFactDefinition("plane_site", "A wreck site in the trees.")

        world.add_definition(ExistsFunctionDefinition())
        world.add_definition(UseFunctionDefinition(character))
        world.add_definition(beach)
        world.add_definition(plane_site)

        escape_module = EscapeModule(beach, plane_site)
        escape_module.apply(world)

        world.add_definition(
            StateWrapperDefinition(AtFactPattern("player", "plane_site"))
        )
        world.add_definition(StateWrapperDefinition(AtFactPattern("battery", "player")))
        metta.run(world.to_metta())

        result = metta.run("!(use (battery plane))")

        self.assertIn(
            "You secure the battery in place. The dead controls shudder back to life, and the plane carries you away from the island.",
            format_metta_output(result),
        )

        game_won_result = metta.run("!(match &self (State (GameWon $reason)) $reason)")
        self.assertEqual(
            unwrap_first_match(game_won_result),
            "You secure the battery in place. The dead controls shudder back to life, and the plane carries you away from the island.",
        )


if __name__ == "__main__":
    unittest.main()
