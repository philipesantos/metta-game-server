from core.definitions.function_definition import FunctionDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.first_function_pattern import FirstFunctionPattern
from core.patterns.functions.last_function_pattern import LastFunctionPattern
from core.patterns.functions.location_path_function_pattern import (
    LocationPathFunctionPattern,
)
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.nlp.nl_spec import NLSpec, SlotSpec


class PickUpFunctionDefinition(FunctionDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self) -> str:
        location_path = LocationPathFunctionPattern("$what")
        first_location = FirstFunctionPattern("$location_path")
        last_location = LastFunctionPattern("$location_path")
        state_at_match = StateWrapperPattern(
            AtFactPattern(self.character.key, "$last_location")
        )
        pickup_event = PickUpEventPattern("$what", "$first_location")
        pickup_trigger = TriggerFunctionPattern(pickup_event)
        # fmt: off
        return (
            f"(= (pickup ($what))\n"
            f"    (let $location_path {location_path.to_metta()}\n"
            f"        (let $first_location {first_location.to_metta()}\n"
            f"            (let $last_location {last_location.to_metta()}\n"
            f"                (if (exists {state_at_match.to_metta()})\n"
            f"                    {pickup_trigger.to_metta()}\n"
            f'                    {ResponseFactPattern(100, '"There is no such item"').to_metta()}\n'
            f"                )\n"
            f"            )\n"
            f"        )\n"
            f"    )\n"
            f")"
        )
        # fmt: on

    def nl_spec(self):
        return NLSpec(
            intent="pickup",
            templates=("pickup {item}", "pick up {item}", "grab {item}"),
            metta="(pickup ({item}))",
            slots={"item": SlotSpec("item")},
        )
