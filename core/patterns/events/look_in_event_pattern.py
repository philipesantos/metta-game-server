from core.patterns.event_pattern import EventPattern


class LookInEventPattern(EventPattern):
    def __init__(self, container: str):
        self.container = container

    def to_metta(self) -> str:
        # fmt: off
        return f"(LookIn {self.container})"
        # fmt: on
