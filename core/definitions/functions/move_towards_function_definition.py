from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.route_fact_pattern import RouteFactPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.definitions.function_definition import FunctionDefinition
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.nlp.nl_spec import NLSpec, SlotSpec


class MoveTowardsFunctionDefinition(FunctionDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self) -> str:
        state_at_match = StateWrapperPattern(AtFactPattern(self.character.key, "$from"))
        route_match = RouteFactPattern("$from", "$direction", "$to")
        move_event = MoveEventPattern("$from", "$to")
        # fmt: off
        return (
            f"(= (move-towards ($direction))\n"
            f"    (match &self {state_at_match.to_metta()}\n"
            f"        (case (match &self {route_match.to_metta()} $to)\n"
            f"        (\n"
            f"            (Empty {ResponseFactPattern(100, '"No way to go there"').to_metta()})\n"
            f"            ($to {TriggerFunctionPattern(move_event).to_metta()})\n"
            f"        ))\n"
            f"    )\n"
            f")"
        )
        # fmt: on

    def nl_spec(self):
        return NLSpec(
            intent="move_towards",
            templates=("go {direction}", "move {direction}", "head {direction}"),
            metta="(move-towards ({direction}))",
            slots={"direction": SlotSpec("direction")},
        )
