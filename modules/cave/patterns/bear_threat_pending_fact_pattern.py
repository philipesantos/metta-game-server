from core.patterns.fact_pattern import FactPattern


class BearThreatPendingFactPattern(FactPattern):
    def __init__(self, character: str):
        self.character = character

    def to_metta(self) -> str:
        # fmt: off
        return f"(BearThreatPending {self.character})"
        # fmt: on
