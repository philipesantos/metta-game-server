from core.definitions.fact_definition import FactDefinition
from core.patterns.facts.container_fact_pattern import ContainerFactPattern
from utils.type import Type


class ContainerFactDefinition(FactDefinition):
    def __init__(self, key: str):
        self.key = key

    def to_metta(self) -> str:
        # fmt: off
        return (
            f"(: {self.key} {Type.CONTAINER.value})\n"
            f"{ContainerFactPattern(self.key).to_metta()}"
        )
        # fmt: on
