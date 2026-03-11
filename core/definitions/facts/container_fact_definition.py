from core.definitions.fact_definition import FactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.side_effects.on_move_show_container_enter_text import (
    OnMoveShowContainerEnterText,
)
from core.definitions.side_effects.on_startup_show_container_enter_text import (
    OnStartupShowContainerEnterText,
)
from core.patterns.events.examine_event_pattern import ExamineEventPattern
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.container_fact_pattern import ContainerFactPattern
from utils.type import Type


class ContainerFactDefinition(FactDefinition):
    NAME_FACT = "ContainerName"
    ENTER_TEXT_FACT = "ContainerEnterText"
    LOOK_TEXT_FACT = "ContainerLookText"
    CONTENTS_TEXT_FACT = "ContainerContentsText"

    def __init__(
        self,
        key: str,
        name: str | None = None,
        text_enter: str | None = None,
        text_examine: str | None = None,
        text_look: str | None = None,
        text_contents: str | None = None,
    ):
        self.key = key
        self.name = name or self._default_name(key)
        self.text_enter = text_enter or self._default_descriptive_text(key)
        self.text_examine = text_examine or self._default_examine_text(key)
        self.text_look = text_look or self._default_look_text(key)
        self.text_contents = text_contents or self._default_contents_text(key)

    def to_metta(self) -> str:
        trigger_examine = TriggerFunctionDefinition(
            ExamineEventPattern(self.key), [OnEventPrint(self.text_examine)]
        )
        trigger_look_in = TriggerFunctionDefinition(
            LookInEventPattern(self.key), [OnEventPrint(self.text_look)]
        )
        trigger_move_show_enter_text = TriggerFunctionDefinition(
            MoveEventPattern("$from", "$to"),
            [OnMoveShowContainerEnterText(self.key, self.text_enter)],
        )
        trigger_startup_show_enter_text = TriggerFunctionDefinition(
            StartupEventPattern(),
            [OnStartupShowContainerEnterText(self.key, self.text_enter)],
        )
        container_name = f"({self.NAME_FACT} {self.key} {self._quote(self.name)})\n"
        container_enter_text = (
            f"({self.ENTER_TEXT_FACT} {self.key} {self._quote(self.text_enter)})\n"
        )
        container_look_text = (
            f"({self.LOOK_TEXT_FACT} {self.key} {self._quote(self.text_look)})\n"
        )
        container_contents_text = (
            f"({self.CONTENTS_TEXT_FACT} {self.key} {self._quote(self.text_contents)})\n"
        )
        # fmt: off
        return (
            f"(: {self.key} {Type.CONTAINER.value})\n"
            f"{ContainerFactPattern(self.key).to_metta()}\n"
            f"{container_name}"
            f"{container_enter_text}"
            f"{container_look_text}"
            f"{container_contents_text}"
            f"{trigger_examine.to_metta()}\n"
            f"{trigger_look_in.to_metta()}\n"
            f"{trigger_move_show_enter_text.to_metta()}\n"
            f"{trigger_startup_show_enter_text.to_metta()}"
        )
        # fmt: on

    @staticmethod
    def _default_descriptive_text(key: str) -> str:
        return f"You notice {ContainerFactDefinition._default_name(key)}."

    @staticmethod
    def _default_examine_text(key: str) -> str:
        return f"You examine {ContainerFactDefinition._default_name(key)}."

    @staticmethod
    def _default_look_text(key: str) -> str:
        return (
            f"You look inside {ContainerFactDefinition._default_name(key)}, "
            f"but there is nothing notable."
        )

    @staticmethod
    def _default_contents_text(key: str) -> str:
        return f"You notice {ContainerFactDefinition._default_name(key)} here."

    @staticmethod
    def _default_name(key: str) -> str:
        return key.replace("_", " ")

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
