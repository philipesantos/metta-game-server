import unittest

from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_startup_show_enter_text import (
    OnStartupShowEnterText,
)
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output


class TestOnStartupShowEnterText(unittest.TestCase):
    def test_returns_item_enter_text_when_present(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

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
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("coin", "glade")).to_metta())
        metta.run(
            StateWrapperDefinition(
                AtFactPattern("hollow_tree_trunk", "glade")
            ).to_metta()
        )
        metta.run(
            TriggerFunctionDefinition(
                StartupEventPattern(), [OnStartupShowEnterText(character)]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(StartupEventPattern())
        result = metta.run(f"!{trigger.to_metta()}")
        result_text = format_metta_output(result)

        self.assertIn("A silver coin glints in the grass.", result_text)
        self.assertNotIn("hollow_tree_trunk", result_text)

    def test_returns_empty_when_no_entities_with_enter_text(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            TriggerFunctionDefinition(
                StartupEventPattern(), [OnStartupShowEnterText(character)]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(StartupEventPattern())
        result = metta.run(f"!{trigger.to_metta()}")

        if result != [[]]:
            self.assertEqual(unwrap_first_match(result), "()")

    def test_returns_character_enter_text_when_present(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(
            CharacterFactDefinition(
                "bear",
                "Bear",
                text_enter="A bear is already here.",
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("bear", "glade")).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                StartupEventPattern(), [OnStartupShowEnterText(character)]
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(StartupEventPattern())
        result = metta.run(f"!{trigger.to_metta()}")
        result_text = format_metta_output(result)

        self.assertIn("A bear is already here.", result_text)


if __name__ == "__main__":
    unittest.main()
