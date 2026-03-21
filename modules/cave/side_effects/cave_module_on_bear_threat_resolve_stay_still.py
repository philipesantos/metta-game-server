from core.definitions.side_effect_definition import SideEffectDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from modules.cave.patterns.bear_threat_pending_fact_pattern import (
    BearThreatPendingFactPattern,
)
from modules.cave.patterns.stay_still_event_pattern import StayStillEventPattern


class CaveModuleOnBearThreatResolveStayStill(SideEffectDefinition):
    def __init__(
        self,
        character: CharacterFactPattern,
        bear_key: str,
        bear_location: str,
        cave_items_to_reveal: list[ItemFactDefinition] | None = None,
    ):
        self.character = character
        self.bear_key = bear_key
        self.bear_location = bear_location
        self.cave_items_to_reveal = cave_items_to_reveal or []

    def to_metta(self, event: StayStillEventPattern) -> str:
        pending_state = StateWrapperPattern(
            BearThreatPendingFactPattern(self.character.key)
        )
        bear_state = StateWrapperPattern(
            AtFactPattern(self.bear_key, self.bear_location)
        )
        visible_item_text = " ".join(
            item.text_enter for item in self.cave_items_to_reveal if item.text_enter
        )
        safe_text = (
            "You remain perfectly still until the bear goes away. You are safe for now."
        )
        if visible_item_text:
            safe_text = f"{safe_text} {visible_item_text}"
        safe_message = ResponseFactPattern(120, self._quote(safe_text))
        stand_still_message = ResponseFactPattern(50, '"You hold still for a moment."')
        # fmt: off
        return (
            f"(if {ExistsFunctionPattern(pending_state).to_metta()}\n"
            f"    (let* ((() (remove-atom &self {pending_state.to_metta()}))\n"
            f"           (() (if {ExistsFunctionPattern(bear_state).to_metta()}\n"
            f"                  (remove-atom &self {bear_state.to_metta()})\n"
            f"                  Empty)))\n"
            f"        {safe_message.to_metta()}\n"
            f"    )\n"
            f"    {stand_still_message.to_metta()}\n"
            f")\n"
        )
        # fmt: on

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
