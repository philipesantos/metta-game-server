import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_move_show_items import OnMoveShowItems
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output


class TestOnMoveShowItems(unittest.TestCase):
    def test_returns_items_when_present(self):
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
        metta.run(ContainerFactDefinition("hollow_tree_trunk").to_metta())
        metta.run(StateWrapperDefinition(AtFactPattern("coin", "glade")).to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern("hollow_tree_trunk", "glade")).to_metta()
        )
        metta.run(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"), [OnMoveShowItems()]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(MoveEventPattern("cave", "glade"))
        result = metta.run(f"!{trigger.to_metta()}")
        result_text = format_metta_output(result)

        self.assertIn("A silver coin glints in the grass.", result_text)
        self.assertIn("You notice hollow_tree_trunk.", result_text)

    def test_returns_empty_when_no_items(self):
        metta = get_test_metta()

        metta.run(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"), [OnMoveShowItems()]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(MoveEventPattern("cave", "glade"))
        result = metta.run(f"!{trigger.to_metta()}")

        if result != [[]]:
            self.assertEqual(unwrap_first_match(result), "Empty")


if __name__ == "__main__":
    unittest.main()
