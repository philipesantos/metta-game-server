from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.facts.supported_use_fact_pattern import SupportedUseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern


class OnUseFallbackPrint(SideEffectDefinition):
    def __init__(self, text: str = "That doesn't seem to do anything."):
        self.text = text

    def to_metta(self, event: UseEventPattern) -> str:
        supported_use = SupportedUseFactPattern(event.what, event.with_what)
        response = ResponseFactPattern(100, f'"{self.text}"').to_metta()
        # Only print the fallback when no concrete use rule exists for this pair.
        return (
            f"(if {ExistsFunctionPattern(supported_use).to_metta()}\n"
            f"    Empty\n"
            f"    {response}\n"
            f")"
        )
