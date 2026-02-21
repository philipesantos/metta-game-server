from core.patterns.fact_pattern import FactPattern
from utils.type import Type


class ContainerFactPattern(FactPattern):
    def __init__(self, key: str):
        self.key = f"{key}"

    def to_metta(self) -> str:
        # fmt: off
        return f"({Type.CONTAINER.value} {self.key})"
        # fmt: on
