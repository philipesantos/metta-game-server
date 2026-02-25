from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


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
            f"    (collapse (match &self {state_at_what.to_metta()}\n"
            f"        (match &self (ItemEnterText $what $text) {ResponseFactPattern(20, '$text').to_metta()})\n"
            f"    ))\n"
            f")"
        )
        # fmt: on
