import unittest

from core.definitions.functions.examine_function_definition import (
    ExamineFunctionDefinition,
)
from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.examine_event_pattern import ExamineEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.examine_function_pattern import ExamineFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match


class TestExamineFunctionDefinition(unittest.TestCase):
    def test_triggers_examine_event_when_item_is_nearby(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(ExamineFunctionDefinition(character).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                ExamineEventPattern("$what"),
                [OnEventPrint("Examined")],
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("compass", "glade")).to_metta())

        examine_action = ExamineFunctionPattern("compass")
        result = metta.run(f"!{examine_action.to_metta()}")

        self.assertEqual(unwrap_first_match(result).text, "Examined")

    def test_returns_message_when_item_missing(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(ExamineFunctionDefinition(character).to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )

        examine_action = ExamineFunctionPattern("compass")
        result = metta.run(f"!{examine_action.to_metta()}")

        self.assertEqual(
            unwrap_first_match(result).text,
            "You do not see anything like that here.",
        )

    def test_triggers_examine_event_when_item_is_in_inventory(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(ExamineFunctionDefinition(character).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                ExamineEventPattern("$what"),
                [OnEventPrint("Examined")],
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern("compass", character.key)).to_metta()
        )

        examine_action = ExamineFunctionPattern("compass")
        result = metta.run(f"!{examine_action.to_metta()}")

        self.assertEqual(unwrap_first_match(result).text, "Examined")


if __name__ == "__main__":
    unittest.main()
