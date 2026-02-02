from core.patterns.fact_pattern import FactPattern


class ResponseFactPattern(FactPattern):
    def __init__(self, priority: int | str, text: str):
        self.priority = f"{priority}"
        self.text = text

    def to_metta(self) -> str:
        # fmt: off
        return f"(Response {self.priority} {self.text})"
        # fmt: on
