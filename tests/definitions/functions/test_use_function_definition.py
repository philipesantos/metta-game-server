import unittest

from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.functions.use_function_definition import UseFunctionDefinition
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.functions.use_function_pattern import UseFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match


class TestUseFunctionDefinition(unittest.TestCase):
    def test_triggers_use_event_when_rules_match(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(UseFunctionDefinition(character).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                UseEventPattern("$what", "$with_what"),
                [OnEventPrint("Used")],
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(
                AtFactPattern("crescent_rock", character.key)
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern("cave_door", "glade")).to_metta()
        )

        use_action = UseFunctionPattern("crescent_rock", "cave_door")
        result = metta.run(f"!{use_action.to_metta()}")

        self.assertEqual(unwrap_first_match(result).text, "Used")

    def test_returns_message_when_item_missing(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(UseFunctionDefinition(character).to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern("cave_door", "glade")).to_metta()
        )

        use_action = UseFunctionPattern("crescent_rock", "cave_door")
        result = metta.run(f"!{use_action.to_metta()}")

        self.assertEqual(unwrap_first_match(result).text, "You do not have that")

    def test_returns_message_when_target_missing(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(UseFunctionDefinition(character).to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(
                AtFactPattern("crescent_rock", character.key)
            ).to_metta()
        )

        use_action = UseFunctionPattern("crescent_rock", "cave_door")
        result = metta.run(f"!{use_action.to_metta()}")

        self.assertEqual(
            unwrap_first_match(result).text, "There is nothing to use that on"
        )


if __name__ == "__main__":
    unittest.main()
