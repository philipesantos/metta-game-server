import unittest

from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.look_in_function_definition import (
    LookInFunctionDefinition,
)
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.look_in_function_pattern import LookInFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match


class TestLookInFunctionDefinition(unittest.TestCase):
    def test_triggers_look_in_event_when_container_is_nearby(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(LookInFunctionDefinition(character).to_metta())
        metta.run(
            TriggerFunctionDefinition(
                LookInEventPattern("$container"),
                [OnEventPrint("Looked")],
            ).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("chest", "glade")).to_metta())

        action = LookInFunctionPattern("chest")
        result = metta.run(f"!{action.to_metta()}")

        self.assertEqual(unwrap_first_match(result).text, "Looked")

    def test_returns_message_when_container_missing(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(LookInFunctionDefinition(character).to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )

        action = LookInFunctionPattern("chest")
        result = metta.run(f"!{action.to_metta()}")

        self.assertEqual(unwrap_first_match(result).text, "There is no such container")


if __name__ == "__main__":
    unittest.main()
