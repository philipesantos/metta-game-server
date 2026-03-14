import unittest

from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.patterns.facts.location_fact_pattern import LocationFactPattern
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern
from core.world import World
from modules.cave.cave_module import CaveModule
from modules.cave.functions.stay_still_function_definition import (
    StayStillFunctionDefinition,
)
from modules.cave.patterns.stay_still_event_pattern import StayStillEventPattern
from modules.cave.patterns.stay_still_function_pattern import (
    StayStillFunctionPattern,
)
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match


class TestCaveModule(unittest.TestCase):
    def test_defines_cave_location_boulder_and_route_block(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition("path_1", "You are in the path 1.")
        character = CharacterFactPattern("player", "John")
        CaveModule(cave_entrance, character).apply(world)
        metta.run(world.to_metta())

        location_pattern = LocationFactPattern("cave")
        location_result = metta.run(
            f"!(match &self {location_pattern.to_metta()} {location_pattern.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(location_result), location_pattern.to_metta())

        bear_pattern = CharacterFactPattern("bear", "Bear")
        bear_result = metta.run(
            f"!(match &self {bear_pattern.to_metta()} {bear_pattern.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(bear_result), bear_pattern.to_metta())

        bear_enter_text_result = metta.run("!(match &self (EnterText bear $text) $text)")
        self.assertEqual(
            unwrap_first_match(bear_enter_text_result),
            "A massive bear looms in the darkness, ready to tear you apart.",
        )

        bear_state = StateWrapperPattern(AtFactPattern("bear", "cave"))
        bear_state_result = metta.run(
            f"!(match &self {bear_state.to_metta()} {bear_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(bear_state_result), bear_state.to_metta())

        boulder_state = StateWrapperPattern(AtFactPattern("huge_rock", "path_1"))
        boulder_result = metta.run(
            f"!(match &self {boulder_state.to_metta()} {boulder_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(boulder_result), boulder_state.to_metta())

        route_block_pattern = RouteBlockFactPattern("path_1", "cave", "$reason")
        route_block_result = metta.run(
            f"!(match &self {route_block_pattern.to_metta()} $reason)"
        )
        self.assertEqual(
            unwrap_first_match(route_block_result),
            "A huge rock blocks the cave entrance.",
        )

    def test_registers_stay_still_function(self):
        world = World()
        cave_entrance = LocationFactDefinition("path_1", "You are in the path 1.")
        character = CharacterFactPattern("player", "John")

        CaveModule(cave_entrance, character).apply(world)

        self.assertTrue(
            any(
                isinstance(definition, StayStillFunctionDefinition)
                for definition in world.definitions
            )
        )

    def test_registers_stay_still_trigger_for_any_location(self):
        world = World()
        cave_entrance = LocationFactDefinition("path_1", "You are in the path 1.")
        character = CharacterFactPattern("player", "John")

        CaveModule(cave_entrance, character).apply(world)

        self.assertTrue(
            any(
                isinstance(definition, TriggerFunctionDefinition)
                and isinstance(definition.event, StayStillEventPattern)
                and definition.event.where == "$where"
                for definition in world.definitions
            )
        )

    def test_stay_still_prints_message_in_non_cave_location(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition("path_1", "You are in the path 1.")
        character = CharacterFactPattern("player", "John")

        CaveModule(cave_entrance, character).apply(world)
        metta.run(world.to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "beach")).to_metta()
        )

        result = metta.run(f"!{StayStillFunctionPattern().to_metta()}")

        self.assertEqual(unwrap_first_match(result).text, "You stand still.")


if __name__ == "__main__":
    unittest.main()
