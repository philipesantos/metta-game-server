from core.definitions.fact_definition import FactDefinition
from core.patterns.facts.response_fact_pattern import ResponseFactPattern


class ResponseFactDefinition(FactDefinition):
    def __init__(self, priority: int | str, text: str):
        self.priority = priority
        self.text = text

    def to_metta(self) -> str:
        # fmt: off
        return ResponseFactPattern(self.priority, self.text).to_metta()
        # fmt: on
