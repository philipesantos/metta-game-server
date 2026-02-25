from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern


class OnLookInShowContainerDescription(SideEffectDefinition):
    def to_metta(self, event: LookInEventPattern) -> str:
        return (
            f"(match &self (ContainerLookText {event.container} $text) "
            f"{ResponseFactPattern(30, '$text').to_metta()})"
        )
