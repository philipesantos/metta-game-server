from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.event_pattern import EventPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern


class OnEventPrint(SideEffectDefinition):
    def __init__(self, text: str, priority: int = 50):
        self.text = text
        self.priority = priority

    def to_metta(self, event: EventPattern) -> str:
        # fmt: off
        return ResponseFactPattern(self.priority, f'"{self.text}"').to_metta()
        # fmt: on
