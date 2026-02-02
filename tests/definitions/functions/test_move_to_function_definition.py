import unittest

from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.definitions.wrappers.log_wrapper_definition import LogWrapperDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.functions.move_to_function_pattern import MoveToFunctionPattern
from tests.utils.metta import get_test_metta

from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.move_to_function_definition import (
    MoveToFunctionDefinition,
)
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from tests.utils.on_move_do_nothing import OnMoveDoNothing
from tests.utils.utils import unwrap_first_match
from utils.direction import Direction


class TestMoveToFunctionDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(MoveToFunctionDefinition(character).to_metta())
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

        metta.run(
            LogWrapperDefinition("0", MoveEventPattern("plane", "cave")).to_metta()
        )
        metta.run(
            LogWrapperDefinition("1", MoveEventPattern("cave", "beach")).to_metta()
        )
        metta.run(
            LogWrapperDefinition("2", MoveEventPattern("beach", "glade")).to_metta()
        )

        state_at = StateWrapperDefinition(AtFactPattern(character.key, "glade"))
        metta.run(state_at.to_metta())

        move_to_cave = MoveToFunctionPattern("cave")
        result_move_to_cave = metta.run(f"!{move_to_cave.to_metta()}")
        self.assertEqual(result_move_to_cave, [[]])

        move_to_plane = MoveToFunctionPattern("plane")
        result_move_to_plane = metta.run(f"!{move_to_plane.to_metta()}")
        self.assertEqual(
            unwrap_first_match(result_move_to_plane).text, "No way to go there"
        )


if __name__ == "__main__":
    unittest.main()
