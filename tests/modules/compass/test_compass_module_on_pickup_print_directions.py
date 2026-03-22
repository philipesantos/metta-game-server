import unittest

from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from modules.compass.functions.compass_directions_function_definition import (
    CompassDirectionsFunctionDefinition,
)
from modules.compass.side_effects.compass_module_on_pickup_print_directions import (
    CompassModuleOnPickupPrintDirections,
)
from tests.utils.metta import get_test_metta
from utils.response import format_metta_output


class TestCompassModuleOnPickupPrintDirections(unittest.TestCase):
    def test_pickup_prints_directions_from_player_location(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(CompassDirectionsFunctionDefinition().to_metta())
        metta.run(
            TriggerFunctionDefinition(
                PickUpEventPattern("compass", "$where"),
                [CompassModuleOnPickupPrintDirections(character)],
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            RouteFactDefinition(
                "glade",
                "north",
                "cave",
                "To the north, a narrow trail rises toward the cave.",
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(PickUpEventPattern("compass", "glade"))
        result = metta.run(f"!{trigger.to_metta()}")
        output_lines = format_metta_output(result).splitlines()

        self.assertEqual(
            output_lines,
            ["To the north, a narrow trail rises toward the cave."],
        )

    def test_pickup_removes_route_blocks_before_printing_directions(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(CompassDirectionsFunctionDefinition().to_metta())
        metta.run(
            TriggerFunctionDefinition(
                PickUpEventPattern("compass", "$where"),
                [
                    CompassModuleOnPickupPrintDirections(
                        character,
                        unblock_location_from="glade",
                    )
                ],
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            RouteFactDefinition(
                "glade",
                "north",
                "cave",
                "To the north, a narrow trail rises toward the cave.",
            ).to_metta()
        )
        metta.run(
            RouteBlockFactDefinition(
                "glade",
                "cave",
                "You hesitate. This isn’t a place to wander blindly.",
            ).to_metta()
        )
        metta.run(
            RouteBlockFactDefinition(
                "glade",
                "beach",
                "You hesitate. This isn’t a place to wander blindly.",
            ).to_metta()
        )
        metta.run(
            RouteBlockFactDefinition(
                "glade",
                "ridge",
                "You hesitate. This isn’t a place to wander blindly.",
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(PickUpEventPattern("compass", "glade"))
        result = metta.run(f"!{trigger.to_metta()}")
        output_lines = format_metta_output(result).splitlines()

        self.assertEqual(
            output_lines,
            ["To the north, a narrow trail rises toward the cave."],
        )

    def test_pickup_uses_player_location_even_when_event_where_is_container(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(CompassDirectionsFunctionDefinition().to_metta())
        metta.run(
            TriggerFunctionDefinition(
                PickUpEventPattern("compass", "$where"),
                [CompassModuleOnPickupPrintDirections(character)],
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            RouteFactDefinition(
                "glade",
                "north",
                "cave",
                "To the north, a narrow trail rises toward the cave.",
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(
            PickUpEventPattern("compass", "unconscious_person")
        )
        result = metta.run(f"!{trigger.to_metta()}")
        output_lines = format_metta_output(result).splitlines()

        self.assertEqual(
            output_lines,
            ["To the north, a narrow trail rises toward the cave."],
        )


if __name__ == "__main__":
    unittest.main()
