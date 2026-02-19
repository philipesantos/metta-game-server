from core.patterns.event_pattern import EventPattern


class ExamineEventPattern(EventPattern):
    def __init__(self, what: str):
        self.what = what

    def to_metta(self) -> str:
        # fmt: off
        return f"(Examine {self.what})"
        # fmt: on
