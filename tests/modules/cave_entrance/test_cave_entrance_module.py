import unittest

from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.use_function_definition import UseFunctionDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.use_function_pattern import UseFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.world import World
from modules.cave_entrance.cave_entrance_module import CaveEntranceModule
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match


class TestCaveEntranceModule(unittest.TestCase):
    def test_places_rock_and_door(self):
        metta = get_test_metta()

        world = World()
        CaveEntranceModule("path_2", "cave").apply(world)
        metta.run(world.to_metta())

        rock_state = StateWrapperPattern(AtFactPattern("crescent_rock", "path_2"))
        rock_result = metta.run(
            f"!(match &self {rock_state.to_metta()} {rock_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(rock_result), rock_state.to_metta())

        door_state = StateWrapperPattern(AtFactPattern("cave_door", "cave"))
        door_result = metta.run(
            f"!(match &self {door_state.to_metta()} {door_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(door_result), door_state.to_metta())

    def test_use_rock_on_door_triggers_event(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        world = World()
        CaveEntranceModule("path_2", "cave").apply(world)
        metta.run(world.to_metta())
        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(UseFunctionDefinition(character).to_metta())

        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "cave")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(
                AtFactPattern("crescent_rock", character.key)
            ).to_metta()
        )

        use_action = UseFunctionPattern("crescent_rock", "cave_door")
        result = metta.run(f"!{use_action.to_metta()}")

        self.assertEqual(unwrap_first_match(result).text, "The cave door opens.")


if __name__ == "__main__":
    unittest.main()
