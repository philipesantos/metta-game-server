from core.patterns.fact_pattern import FactPattern


class GameWonFactPattern(FactPattern):
    def __init__(self, reason: str):
        self.reason = reason

    def to_metta(self) -> str:
        # fmt: off
        return f"(GameWon {self.reason})"
        # fmt: on
