from core.patterns.fact_pattern import FactPattern


class CaveLitFactPattern(FactPattern):
    def __init__(self, location: str):
        self.location = location

    def to_metta(self) -> str:
        # fmt: off
        return f"(CaveLit {self.location})"
        # fmt: on
