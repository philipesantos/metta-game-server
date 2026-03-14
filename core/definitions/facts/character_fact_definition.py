from core.definitions.fact_definition import FactDefinition
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from utils.type import Type


class CharacterFactDefinition(FactDefinition):
    ENTER_TEXT_FACT = "EnterText"
    ENTER_PRIORITY_FACT = "EnterPriority"

    def __init__(
        self,
        key: str,
        name: str,
        text_enter: str | None = None,
        enter_priority: int = 20,
    ):
        self.key = f"{key}"
        self.name = name
        self.text_enter = text_enter
        self.enter_priority = enter_priority

    def to_pattern(self):
        return CharacterFactPattern(self.key, self.name)

    def to_metta(self) -> str:
        character_enter_text = (
            f"({self.ENTER_TEXT_FACT} {self.key} {self._quote(self.text_enter)})\n"
            if self.text_enter is not None
            else ""
        )
        character_enter_priority = (
            f"({self.ENTER_PRIORITY_FACT} {self.key} {self.enter_priority})\n"
            if self.text_enter is not None
            else ""
        )
        # fmt: off
        return (
            f"(: {self.key} {Type.CHARACTER.value})\n"
            f"{character_enter_text}"
            f"{character_enter_priority}"
            f"{self.to_pattern().to_metta()}"
        )
        # fmt: on

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
