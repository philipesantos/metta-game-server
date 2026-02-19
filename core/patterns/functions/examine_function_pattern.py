from core.patterns.function_pattern import FunctionPattern


class ExamineFunctionPattern(FunctionPattern):
    def __init__(self, what: str):
        self.what = what

    def to_metta(self) -> str:
        # fmt: off
        return f"(examine ({self.what}))"
        # fmt: on
