import unittest

from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_move_show_enter_text import OnMoveShowEnterText
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output


class TestOnMoveShowEnterText(unittest.TestCase):
    def test_does_not_show_default_text_when_item_has_no_enter_text(self):
        metta = get_test_metta()

        metta.run(
            ItemFactDefinition(
                "coin",
                "picked",
                "dropped",
                "examined",
            ).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("coin", "glade")).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"), [OnMoveShowEnterText()]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(MoveEventPattern("cave", "glade"))
        result = metta.run(f"!{trigger.to_metta()}")

        if result != [[]]:
            self.assertEqual(unwrap_first_match(result), "()")

    def test_returns_item_enter_text_when_present(self):
        metta = get_test_metta()

        metta.run(
            ItemFactDefinition(
                "coin",
                "picked",
                "dropped",
                "examined",
                text_enter="A silver coin glints in the grass.",
            ).to_metta()
        )
        metta.run(
            ContainerFactDefinition(
                "hollow_tree_trunk",
                text_contents="A hollow tree trunk stands nearby.",
            ).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("coin", "glade")).to_metta())
        metta.run(
            StateWrapperDefinition(
                AtFactPattern("hollow_tree_trunk", "glade")
            ).to_metta()
        )
        metta.run(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"), [OnMoveShowEnterText()]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(MoveEventPattern("cave", "glade"))
        result = metta.run(f"!{trigger.to_metta()}")
        result_text = format_metta_output(result)

        self.assertIn("A silver coin glints in the grass.", result_text)
        self.assertNotIn("hollow_tree_trunk", result_text)

    def test_returns_character_enter_text_when_present(self):
        metta = get_test_metta()

        metta.run(
            CharacterFactDefinition(
                "bear",
                "Bear",
                text_enter="A bear is waiting in the clearing.",
            ).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("bear", "glade")).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"), [OnMoveShowEnterText()]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(MoveEventPattern("cave", "glade"))
        result = metta.run(f"!{trigger.to_metta()}")
        result_text = format_metta_output(result)

        self.assertIn("A bear is waiting in the clearing.", result_text)

    def test_returns_empty_when_no_entities_with_enter_text(self):
        metta = get_test_metta()

        metta.run(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"), [OnMoveShowEnterText()]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(MoveEventPattern("cave", "glade"))
        result = metta.run(f"!{trigger.to_metta()}")

        if result != [[]]:
            self.assertEqual(unwrap_first_match(result), "()")


if __name__ == "__main__":
    unittest.main()
