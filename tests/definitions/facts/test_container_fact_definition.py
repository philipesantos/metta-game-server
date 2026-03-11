import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.examine_event_pattern import ExamineEventPattern
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.container_fact_pattern import ContainerFactPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.location_fact_pattern import LocationFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output
from utils.type import Type


class TestContainerFactDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        key = "chest"
        name = "Wooden chest"
        text_enter = "A weathered chest sits in the corner."
        text_examine = "The lid is warped and bound with rusted iron."
        text_look = "Inside, the chest smells of cedar."
        text_contents = "A weathered chest sits beneath the window."
        metta.run(
            ContainerFactDefinition(
                key,
                name=name,
                text_enter=text_enter,
                text_examine=text_examine,
                text_look=text_look,
                text_contents=text_contents,
            ).to_metta()
        )

        result_type = metta.run(f"!(get-type {key})")
        self.assertEqual(unwrap_first_match(result_type), Type.CONTAINER.value)

        container_key = ContainerFactPattern("$key")
        result_key = metta.run(f"!(match &self {container_key.to_metta()} $key)")
        self.assertEqual(unwrap_first_match(result_key), key)

        result_enter_text = metta.run(
            f"!(match &self (ContainerEnterText {key} $text) $text)"
        )
        self.assertEqual(unwrap_first_match(result_enter_text), text_enter)

        result_look_text = metta.run(
            f"!(match &self (ContainerLookText {key} $text) $text)"
        )
        self.assertEqual(unwrap_first_match(result_look_text), text_look)

        result_contents_text = metta.run(
            f"!(match &self (ContainerContentsText {key} $text) $text)"
        )
        self.assertEqual(unwrap_first_match(result_contents_text), text_contents)

        result_name = metta.run(f"!(match &self (ContainerName {key} $name) $name)")
        self.assertEqual(unwrap_first_match(result_name), name)

        examine_trigger = TriggerFunctionPattern(ExamineEventPattern(key))
        result_examine = metta.run(f"!{examine_trigger.to_metta()}")
        self.assertEqual(format_metta_output(result_examine), text_examine)

        look_in_trigger = TriggerFunctionPattern(LookInEventPattern(key))
        result_look_in = metta.run(f"!{look_in_trigger.to_metta()}")
        self.assertEqual(format_metta_output(result_look_in), text_look)

        metta.run(StateWrapperDefinition(AtFactPattern(key, "glade")).to_metta())
        move_trigger = TriggerFunctionPattern(MoveEventPattern("cave", "glade"))
        result_move = metta.run(f"!{move_trigger.to_metta()}")
        self.assertIn(text_enter, format_metta_output(result_move))

        metta.run(StateWrapperDefinition(AtFactPattern("player", "glade")).to_metta())
        startup_trigger = TriggerFunctionPattern(StartupEventPattern())
        result_startup = metta.run(f"!{startup_trigger.to_metta()}")
        self.assertIn(text_enter, format_metta_output(result_startup))

        no_match = LocationFactPattern("bottle")
        result_no_match = metta.run(f"!(match &self {no_match.to_metta()} True)")
        self.assertEqual(result_no_match, [[]])


if __name__ == "__main__":
    unittest.main()
