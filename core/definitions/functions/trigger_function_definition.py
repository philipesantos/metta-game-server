from core.patterns.event_pattern import EventPattern
from core.definitions.function_definition import FunctionDefinition
from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.use_item_event_pattern import UseItemEventPattern
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.supported_single_use_fact_pattern import (
    SupportedSingleUseFactPattern,
)
from core.patterns.facts.supported_use_fact_pattern import SupportedUseFactPattern


class TriggerFunctionDefinition(FunctionDefinition):
    def __init__(self, event: EventPattern, side_effects: list[SideEffectDefinition]):
        self.event = event
        self.side_effects = side_effects

    def to_metta(self) -> str:
        def indent_block(text: str, indent: str = "    ") -> str:
            return "\n".join(
                (indent + line) if line else line for line in text.splitlines()
            )

        metadata = self._metadata()
        # fmt: off
        trigger_rules = "\n".join(
            (
                f"(= (trigger {self.event.to_metta()})\n"
                f"{indent_block(side_effect.to_metta(self.event))}\n"
                f")"
            )
            for side_effect in self.side_effects
        )
        if metadata:
            return f"{metadata}\n{trigger_rules}"
        return trigger_rules
        # fmt: on

    def _metadata(self) -> str:
        if not isinstance(self.event, UseEventPattern):
            if not isinstance(self.event, UseItemEventPattern):
                return ""
            if self._is_variable(self.event.what):
                return ""
            return SupportedSingleUseFactPattern(self.event.what).to_metta()
        if self._is_variable(self.event.what) or self._is_variable(
            self.event.with_what
        ):
            return ""
        return SupportedUseFactPattern(self.event.what, self.event.with_what).to_metta()

    @staticmethod
    def _is_variable(value: str) -> bool:
        return value.startswith("$")
