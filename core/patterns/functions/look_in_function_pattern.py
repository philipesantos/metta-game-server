from core.patterns.function_pattern import FunctionPattern


class LookInFunctionPattern(FunctionPattern):
    def __init__(self, container: str):
        self.container = container

    def to_metta(self) -> str:
        # fmt: off
        return f"(look-in ({self.container}))"
        # fmt: on
