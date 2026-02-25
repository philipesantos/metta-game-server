import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_look_in_show_container_description import (
    OnLookInShowContainerDescription,
)
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta
from utils.response import format_metta_output


class TestOnLookInShowContainerDescription(unittest.TestCase):
    def test_shows_container_description_when_present(self):
        metta = get_test_metta()

        description = "You check the unconscious person. Their breathing is shallow but steady."
        metta.run(
            ContainerFactDefinition(
                "unconscious_person",
                text_look=description,
            ).to_metta()
        )
        metta.run(
            TriggerFunctionDefinition(
                LookInEventPattern("$container"),
                [OnLookInShowContainerDescription()],
            ).to_metta()
        )

        trigger = TriggerFunctionPattern(LookInEventPattern("unconscious_person"))
        result = metta.run(f"!{trigger.to_metta()}")

        self.assertEqual(format_metta_output(result), description)


if __name__ == "__main__":
    unittest.main()
