from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from utils.type import Type


class OnLookInShowItems(SideEffectDefinition):
    def to_metta(self, event: LookInEventPattern) -> str:
        state_at_item = StateWrapperPattern(AtFactPattern("$item", event.container))
        # fmt: off
        return (
            f"(let $result (collapse (match &self {state_at_item.to_metta()}\n"
            f"    (case (get-type $item) (\n"
            f"        ({Type.ITEM.value} (match &self (ItemLookText $item $text)\n"
            f"            (let $priority_result (match &self (ItemLookPriority $item $priority) $priority)\n"
            f"                (case $priority_result (\n"
            f"                    (Empty {ResponseFactPattern(20, '$text').to_metta()})\n"
            f"                    ($priority {ResponseFactPattern('$priority', '$text').to_metta()})\n"
            f"                ))\n"
            f"            )\n"
            f"        ))\n"
            f"        ({Type.CONTAINER.value} (match &self (ContainerContentsText $item $text) {ResponseFactPattern(20, '$text').to_metta()}))\n"
            f"        ($_ Empty)\n"
            f"    ))\n"
            f"))\n"
            f"    (case $result\n"
            f"    (\n"
            f'        (() {ResponseFactPattern(20, "\"It is empty.\"").to_metta()})\n'
            f"        ($_ $result)\n"
            f"    ))\n"
            f")"
        )
        # fmt: on
