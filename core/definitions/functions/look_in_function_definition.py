from core.definitions.function_definition import FunctionDefinition
from core.nlp.nl_spec import NLSpec, SlotSpec
from core.patterns.events.look_in_event_pattern import LookInEventPattern
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


class LookInFunctionDefinition(FunctionDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self) -> str:
        location_path = LocationPathFunctionPattern("$container")
        last_location = LastFunctionPattern("$location_path")
        state_at_player = StateWrapperPattern(
            AtFactPattern(self.character.key, "$where")
        )
        state_container_exists = StateWrapperPattern(
            AtFactPattern("$container", "$container_where")
        )
        state_at_container = StateWrapperPattern(
            AtFactPattern(self.character.key, "$last_location")
        )
        look_in_event = LookInEventPattern("$container")
        look_in_trigger = TriggerFunctionPattern(look_in_event)
        # fmt: off
        return (
            f"(= (look-in ($container))\n"
            f"    (let $where (match &self {state_at_player.to_metta()} $where)\n"
            f"        (if {ExistsFunctionPattern(state_container_exists).to_metta()}\n"
            f"            (let $location_path {location_path.to_metta()}\n"
            f"                (let $last_location {last_location.to_metta()}\n"
            f"                    (if {ExistsFunctionPattern(state_at_container).to_metta()}\n"
            f"                        {look_in_trigger.to_metta()}\n"
            f'                        {ResponseFactPattern(100, '"There is no such container"').to_metta()}\n'
            f"                    )\n"
            f"                )\n"
            f"            )\n"
            f'            {ResponseFactPattern(100, '"There is no such container"').to_metta()}\n'
            f"        )\n"
            f"    )\n"
            f")"
        )
        # fmt: on

    def nl_spec(self):
        return NLSpec(
            intent="look_in",
            templates=(
                "look in {container}",
                "look inside {container}",
                "check inside {container}",
                "search {container}",
            ),
            metta="(look-in ({container}))",
            slots={"container": SlotSpec("container")},
        )
