from core.definitions.fact_definition import FactDefinition
from core.patterns.facts.container_fact_pattern import ContainerFactPattern
from utils.type import Type


class ContainerFactDefinition(FactDefinition):
    NAME_FACT = "ContainerName"
    ENTER_TEXT_FACT = "ContainerEnterText"
    LOOK_TEXT_FACT = "ContainerLookText"

    def __init__(
        self,
        key: str,
        name: str | None = None,
        text_enter: str | None = None,
        text_look: str | None = None,
    ):
        self.key = key
        self.name = name or self._default_name(key)
        self.text_enter = text_enter or self._default_descriptive_text(key)
        self.text_look = text_look or self._default_descriptive_text(key)

    def to_metta(self) -> str:
        container_name = f'({self.NAME_FACT} {self.key} {self._quote(self.name)})\n'
        container_enter_text = (
            f'({self.ENTER_TEXT_FACT} {self.key} {self._quote(self.text_enter)})\n'
        )
        container_look_text = (
            f'({self.LOOK_TEXT_FACT} {self.key} {self._quote(self.text_look)})\n'
        )
        # fmt: off
        return (
            f"(: {self.key} {Type.CONTAINER.value})\n"
            f"{ContainerFactPattern(self.key).to_metta()}\n"
            f"{container_name}"
            f"{container_enter_text}"
            f"{container_look_text}"
        )
        # fmt: on

    @staticmethod
    def _default_descriptive_text(key: str) -> str:
        return f"You notice {ContainerFactDefinition._default_name(key)}."

    @staticmethod
    def _default_name(key: str) -> str:
        return key.replace("_", " ")

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
