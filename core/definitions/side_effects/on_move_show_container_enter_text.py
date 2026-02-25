from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class OnMoveShowContainerEnterText(SideEffectDefinition):
    def __init__(self, container_key: str, text_enter: str):
        self.container_key = container_key
        self.text_enter = text_enter

    def to_metta(self, event: MoveEventPattern) -> str:
        state_at_container = StateWrapperPattern(
            AtFactPattern(self.container_key, event.to_location)
        )
        return (
            f"(if {ExistsFunctionPattern(state_at_container).to_metta()} "
            f"{ResponseFactPattern(20, self._quote(self.text_enter)).to_metta()} "
            f"Empty)"
        )

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
