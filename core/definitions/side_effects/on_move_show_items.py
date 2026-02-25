from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class OnMoveShowItems(SideEffectDefinition):
    def to_metta(self, event: MoveEventPattern) -> str:
        state_at_what = StateWrapperPattern(AtFactPattern("$what", event.to_location))
        # fmt: off
        return (
            f"(collapse (match &self {state_at_what.to_metta()}\n"
            f"    (match &self (ItemEnterText $what $text) {ResponseFactPattern(20, '$text').to_metta()})\n"
            f"))"
        )
        # fmt: on
