import unittest

from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_startup_show_items import OnStartupShowItems
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match


class TestOnStartupShowItems(unittest.TestCase):
    def test_returns_items_when_present(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ItemFactDefinition("coin", "picked", "dropped").to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("coin", "glade")).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                StartupEventPattern(), [OnStartupShowItems(character)]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(StartupEventPattern())
        result = metta.run(f"!{trigger.to_metta()}")
        result_value = unwrap_first_match(result)
        result_text = result_value.text if hasattr(result_value, "text") else result_value

        self.assertIn("You see:", result_text)
        self.assertIn("coin", result_text)

    def test_returns_empty_when_no_items(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            TriggerFunctionDefinition(
                StartupEventPattern(), [OnStartupShowItems(character)]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(StartupEventPattern())
        result = metta.run(f"!{trigger.to_metta()}")

        if result != [[]]:
            self.assertEqual(unwrap_first_match(result), "Empty")


if __name__ == "__main__":
    unittest.main()
