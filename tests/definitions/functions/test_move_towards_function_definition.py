import unittest

from core.definitions.facts.at_fact_definition import AtFactDefinition
from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.functions.move_towards_function_pattern import (
    MoveTowardsFunctionPattern,
)
from tests.utils.metta import get_test_metta

from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.definitions.functions.move_towards_function_definition import (
    MoveTowardsFunctionDefinition,
)
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from tests.utils.on_move_do_nothing import OnMoveDoNothing
from tests.utils.utils import unwrap_first_match
from utils.direction import Direction


class TestMoveTowardsFunctionDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(MoveTowardsFunctionDefinition(character).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"), [OnMoveDoNothing()]
            ).to_metta()
        )

        metta.run(
            RouteFactDefinition("cave", Direction.NORTH.value, "beach").to_metta()
        )
        metta.run(
            RouteFactDefinition("beach", Direction.NORTH.value, "glade").to_metta()
        )
        metta.run(
            RouteFactDefinition("glade", Direction.SOUTH.value, "beach").to_metta()
        )
        metta.run(
            RouteFactDefinition("beach", Direction.SOUTH.value, "cave").to_metta()
        )
        metta.run(
            RouteFactDefinition("cave", Direction.SOUTH.value, "plane").to_metta()
        )

        metta.run(AtFactDefinition(character.key, "cave").to_metta())
        metta.run(AtFactDefinition(character.key, "beach").to_metta())
        metta.run(AtFactDefinition(character.key, "glade").to_metta())

        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )

        move_towards_west = MoveTowardsFunctionPattern(Direction.WEST)
        result_move_towards_west = metta.run(f"!{move_towards_west.to_metta()}")
        self.assertEqual(
            unwrap_first_match(result_move_towards_west).text, "No way to go there"
        )

        move_towards_south = MoveTowardsFunctionPattern(Direction.SOUTH)
        result_move_towards_south = metta.run(f"!{move_towards_south.to_metta()}")
        self.assertEqual(result_move_towards_south, [[]])


if __name__ == "__main__":
    unittest.main()
