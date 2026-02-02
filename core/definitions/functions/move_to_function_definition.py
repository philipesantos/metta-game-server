from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.definitions.function_definition import FunctionDefinition
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.wrappers.log_wrapper_pattern import LogWrapperPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.nlp.nl_spec import NLSpec, SlotSpec


class MoveToFunctionDefinition(FunctionDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self) -> str:
        state_at_match = StateWrapperPattern(AtFactPattern(self.character.key, "$from"))
        log_move_event_match = LogWrapperPattern("$tick", MoveEventPattern("$_", "$to"))
        move_event_trigger = MoveEventPattern("$from", "$to")
        # fmt: off
        return (
            f"(= (move-to ($to))\n"
            f"    (match &self {state_at_match.to_metta()}\n"
            f"        (if {ExistsFunctionPattern(log_move_event_match).to_metta()}\n"
            f"            {TriggerFunctionPattern(move_event_trigger).to_metta()}\n"
            f"            {ResponseFactPattern(100, '"No way to go there"').to_metta()}\n"
            f"        )\n"
            f"    )\n"
            f")"
        )
        # fmt: on

    def nl_spec(self):
        return NLSpec(
            intent="move_to",
            templates=("go to {location}", "move to {location}", "walk to {location}"),
            metta="(move-to ({location}))",
            slots={"location": SlotSpec("location")},
        )
