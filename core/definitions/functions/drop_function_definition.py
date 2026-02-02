from core.definitions.function_definition import FunctionDefinition
from core.patterns.events.drop_event_pattern import DropEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.functions.last_function_pattern import LastFunctionPattern
from core.patterns.functions.location_path_function_pattern import (
    LocationPathFunctionPattern,
)
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.nlp.nl_spec import NLSpec, SlotSpec


class DropFunctionDefinition(FunctionDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self) -> str:
        state_at_match = StateWrapperPattern(AtFactPattern("$what", self.character.key))
        state_at_exists = ExistsFunctionPattern(state_at_match)
        location_path = LocationPathFunctionPattern(self.character.key)
        last_location = LastFunctionPattern(location_path.to_metta())
        drop_event = DropEventPattern("$what", last_location.to_metta())
        drop_trigger = TriggerFunctionPattern(drop_event)
        # fmt: off
        return (
            f"(= (drop ($what))\n"
            f"    (if {state_at_exists.to_metta()}\n"
            f"        {drop_trigger.to_metta()}\n"
            f'        {ResponseFactPattern(100, '"You do not have that item"').to_metta()}\n'
            f"    )\n"
            f")"
        )
        # fmt: on

    def nl_spec(self):
        return NLSpec(
            intent="drop",
            templates=("drop {item}", "leave {item}"),
            metta="(drop ({item}))",
            slots={"item": SlotSpec("item")},
        )
