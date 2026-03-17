from core.patterns.fact_pattern import FactPattern


class SupportedUseFactPattern(FactPattern):
    def __init__(self, what: str, with_what: str):
        self.what = what
        self.with_what = with_what

    def to_metta(self) -> str:
        # fmt: off
        return f"(SupportedUse {self.what} {self.with_what})"
        # fmt: on
