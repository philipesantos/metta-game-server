from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from utils.type import Type


class OnStartupShowItems(SideEffectDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self, event: StartupEventPattern) -> str:
        state_at_player = StateWrapperPattern(
            AtFactPattern(self.character.key, "$where")
        )
        state_at_what = StateWrapperPattern(AtFactPattern("$what", "$where"))
        # fmt: off
        return (
            f"(let $where (match &self {state_at_player.to_metta()} $where)\n"
            f"    (let $result (collapse (match &self {state_at_what.to_metta()}\n"
            f"        (case (get-type $what) (\n"
            f"            ({Type.ITEM.value} $what)\n"
            f"            ({Type.CONTAINER.value} $what)\n"
            f"            ($_ Empty)\n"
            f"        ))\n"
            f"    ))\n"
            f"        (case $result\n"
            f"        (\n"
            f"            (() Empty)\n"
            f"            ($_ {ResponseFactPattern(20, '(Text \"You see: \" $result)').to_metta()})\n"
            f"        ))\n"
            f"    )\n"
            f")"
        )
        # fmt: on
