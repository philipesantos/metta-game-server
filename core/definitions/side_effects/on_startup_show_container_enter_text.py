from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class OnStartupShowContainerEnterText(SideEffectDefinition):
    def __init__(self, container_key: str, text_enter: str, character_key: str = "player"):
        self.container_key = container_key
        self.text_enter = text_enter
        self.character_key = character_key

    def to_metta(self, event: StartupEventPattern) -> str:
        state_at_player = StateWrapperPattern(AtFactPattern(self.character_key, "$where"))
        state_at_container = StateWrapperPattern(AtFactPattern(self.container_key, "$where"))
        return (
            f"(let $where (match &self {state_at_player.to_metta()} $where)\n"
            f"    (if {ExistsFunctionPattern(state_at_container).to_metta()}\n"
            f"        {ResponseFactPattern(20, self._quote(self.text_enter)).to_metta()}\n"
            f"        Empty\n"
            f"    )\n"
            f")"
        )

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
