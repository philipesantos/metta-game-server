from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.item_fact_pattern import ItemFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class OnMoveShowItems(SideEffectDefinition):
    def to_metta(self, event: MoveEventPattern) -> str:
        state_at_item = StateWrapperPattern(AtFactPattern("$item", event.to_location))
        item_fact = ItemFactPattern("$item")
        # fmt: off
        return (
            f"(let $result (collapse (match &self {state_at_item.to_metta()}\n"
            f"    (match &self {item_fact.to_metta()} $item)\n"
            f"))\n"
            f"    (case $result\n"
            f"    (\n"
            f"        (() Empty)\n"
            f"        ($_ {ResponseFactPattern(20, '("You see: " $result)').to_metta()})\n"
            f"    ))\n"
            f")"
        )
        # fmt: on
