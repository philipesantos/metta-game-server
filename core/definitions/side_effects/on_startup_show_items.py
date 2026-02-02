from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.item_fact_pattern import ItemFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class OnStartupShowItems(SideEffectDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self, event: StartupEventPattern) -> str:
        state_at_player = StateWrapperPattern(
            AtFactPattern(self.character.key, "$where")
        )
        state_at_item = StateWrapperPattern(AtFactPattern("$item", "$where"))
        item_fact = ItemFactPattern("$item")
        # fmt: off
        return (
            f"(let $where (match &self {state_at_player.to_metta()} $where)\n"
            f"    (let $result (collapse (match &self {state_at_item.to_metta()}\n"
            f"        (match &self {item_fact.to_metta()} $item)\n"
            f"    ))\n"
            f"        (case $result\n"
            f"        (\n"
            f"            (() Empty)\n"
            f"            ($_ {ResponseFactPattern(20, '("You see: " $result)').to_metta()})\n"
            f"        ))\n"
            f"    )\n"
            f")"
        )
        # fmt: on
