import unittest

from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from modules.compass.side_effects.compass_module_on_move_print_directions import (
    CompassModuleOnMovePrintDirections,
)
from modules.compass.functions.compass_directions_function_definition import (
    CompassDirectionsFunctionDefinition,
)
from tests.utils.metta import get_test_metta
from utils.response import format_metta_output


class TestCompassModuleOnMovePrintDirections(unittest.TestCase):
    def _register_compass_trigger(self, metta, character):
        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(CompassDirectionsFunctionDefinition().to_metta())
        metta.run(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"),
                [CompassModuleOnMovePrintDirections(character)],
            ).to_metta()
        )

    def test_returns_directions_when_player_has_compass(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        self._register_compass_trigger(metta, character)
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern("compass", character.key)).to_metta()
        )
        metta.run(
            RouteFactDefinition(
                "cave",
                "north",
                "glade",
                "To the north, a steep trail climbs back toward the glade.",
            ).to_metta()
        )
        metta.run(
            RouteFactDefinition(
                "cave",
                "east",
                "beach",
                "To the east, a narrow passage slopes toward the beach.",
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(MoveEventPattern("glade", "cave"))
        result = metta.run(f"!{trigger.to_metta()}")
        output_lines = format_metta_output(result).splitlines()

        self.assertIn(
            "To the north, a steep trail climbs back toward the glade.",
            output_lines,
        )
        self.assertIn(
            "To the east, a narrow passage slopes toward the beach.",
            output_lines,
        )
        self.assertEqual(len(output_lines), 2)

    def test_returns_empty_when_player_lacks_compass(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        self._register_compass_trigger(metta, character)
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(RouteFactDefinition("glade", "north", "cave").to_metta())

        trigger = TriggerFunctionPattern(MoveEventPattern("glade", "cave"))
        result = metta.run(f"!{trigger.to_metta()}")

        self.assertEqual(result, [[]])

    def test_hides_blocked_route_descriptions(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        self._register_compass_trigger(metta, character)
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "ridge")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern("compass", character.key)).to_metta()
        )
        metta.run(
            RouteFactDefinition("ridge", "north", "cave").to_metta()
        )
        metta.run(
            RouteFactDefinition("ridge", "south", "glade").to_metta()
        )
        metta.run(
            RouteFactDefinition(
                "cave",
                "south",
                "ridge",
                "To the south, the path returns to the ridge.",
            ).to_metta()
        )
        metta.run(
            RouteFactDefinition(
                "ridge",
                "north",
                "cave",
                "To the north, the cave mouth opens beyond a giant boulder.",
            ).to_metta()
        )
        metta.run(
            RouteFactDefinition(
                "ridge",
                "south",
                "glade",
                "To the south, the trail slopes back toward the glade.",
            ).to_metta()
        )
        metta.run(
            RouteBlockFactDefinition(
                "ridge",
                "cave",
                "A huge rock blocks the cave entrance.",
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(MoveEventPattern("glade", "ridge"))
        result = metta.run(f"!{trigger.to_metta()}")
        output_lines = format_metta_output(result).splitlines()

        self.assertNotIn(
            "To the north, the cave mouth opens beyond a giant boulder.",
            output_lines,
        )
        self.assertIn(
            "To the south, the trail slopes back toward the glade.",
            output_lines,
        )
        self.assertEqual(len(output_lines), 1)


if __name__ == "__main__":
    unittest.main()
