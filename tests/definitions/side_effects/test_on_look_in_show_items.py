import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_look_in_show_items import OnLookInShowItems
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output


class TestOnLookInShowItems(unittest.TestCase):
    def test_shows_items_inside_container(self):
        metta = get_test_metta()

        metta.run(
            ItemFactDefinition(
                "coin",
                "picked",
                "dropped",
                "examined",
                text_look="A silver coin glints inside.",
            ).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("coin", "chest")).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                LookInEventPattern("$container"), [OnLookInShowItems()]
            ).to_metta()
        )

        trigger_look_in = TriggerFunctionPattern(LookInEventPattern("chest"))
        result = metta.run(f"!{trigger_look_in.to_metta()}")

        self.assertEqual(format_metta_output(result), "A silver coin glints inside.")

    def test_shows_empty_message_when_no_items_inside(self):
        metta = get_test_metta()

        metta.run(
            TriggerFunctionDefinition(
                LookInEventPattern("$container"), [OnLookInShowItems()]
            ).to_metta()
        )

        trigger_look_in = TriggerFunctionPattern(LookInEventPattern("chest"))
        result = metta.run(f"!{trigger_look_in.to_metta()}")

        self.assertEqual(unwrap_first_match(result).text, "It is empty.")

    def test_shows_container_contents_text_for_nested_container(self):
        metta = get_test_metta()

        metta.run(
            ContainerFactDefinition(
                "fireplace",
                text_look="You peer inside the fireplace.",
                text_contents="A cold stone fireplace is built into the far wall.",
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern("fireplace", "cabin")).to_metta()
        )
        metta.run(
            TriggerFunctionDefinition(
                LookInEventPattern("$container"), [OnLookInShowItems()]
            ).to_metta()
        )

        result = metta.run(
            f"!{TriggerFunctionPattern(LookInEventPattern('cabin')).to_metta()}"
        )

        self.assertEqual(
            format_metta_output(result),
            "A cold stone fireplace is built into the far wall.",
        )


if __name__ == "__main__":
    unittest.main()
