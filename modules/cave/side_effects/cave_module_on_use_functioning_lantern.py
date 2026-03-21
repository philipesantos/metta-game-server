from core.definitions.side_effect_definition import SideEffectDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.patterns.events.use_item_event_pattern import UseItemEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from modules.cave.patterns.bear_threat_pending_fact_pattern import (
    BearThreatPendingFactPattern,
)
from modules.cave.patterns.cave_lit_fact_pattern import CaveLitFactPattern


class CaveModuleOnUseFunctioningLantern(SideEffectDefinition):
    def __init__(
        self,
        character: CharacterFactPattern,
        cave_location: str,
        bear_key: str,
        cave_items_to_reveal: list[ItemFactDefinition] | None = None,
    ):
        self.character = character
        self.cave_location = cave_location
        self.bear_key = bear_key
        self.cave_items_to_reveal = cave_items_to_reveal or []

    def to_metta(self, event: UseItemEventPattern) -> str:
        player_in_cave = StateWrapperPattern(
            AtFactPattern(self.character.key, self.cave_location)
        )
        bear_state = StateWrapperPattern(
            AtFactPattern(self.bear_key, self.cave_location)
        )
        pending_state = StateWrapperPattern(
            BearThreatPendingFactPattern(self.character.key)
        )
        lantern_state = StateWrapperPattern(
            AtFactPattern(event.what, self.character.key)
        )
        cave_lit_state = StateWrapperPattern(CaveLitFactPattern(self.cave_location))
        visible_message = ResponseFactPattern(
            120,
            '"The lantern light spills across damp stone walls and old bones scattered across the cave floor."',
        )
        reveal_message = ResponseFactPattern(
            120,
            '"The lantern light spills across damp stone walls and old bones scattered across the cave floor. A massive bear looms in the darkness, ready to tear you apart."',
        )
        no_use_message = ResponseFactPattern(100, '"The lantern has no use here."')
        reveal_item_updates = "".join(
            f"               (() (add-atom &self {StateWrapperPattern(AtFactPattern(item.key, self.cave_location)).to_metta()}))\n"
            for item in self.cave_items_to_reveal
        )
        # fmt: off
        return (
            f"(if {ExistsFunctionPattern(player_in_cave).to_metta()}\n"
            f"    (if {ExistsFunctionPattern(cave_lit_state).to_metta()}\n"
            f"        (let* ((() (remove-atom &self {lantern_state.to_metta()})))\n"
            f"            {visible_message.to_metta()}\n"
            f"        )\n"
            f"        (let* ((() (remove-atom &self {lantern_state.to_metta()}))\n"
            f"               (() (add-atom &self {cave_lit_state.to_metta()}))\n"
            f"               (() (add-atom &self {bear_state.to_metta()}))\n"
            f"{reveal_item_updates}"
            f"               (() (if {ExistsFunctionPattern(pending_state).to_metta()}\n"
            f"                      Empty\n"
            f"                      (add-atom &self {pending_state.to_metta()}))))\n"
            f"            {reveal_message.to_metta()}\n"
            f"        )\n"
            f"    )\n"
            f"    {no_use_message.to_metta()}\n"
            f")\n"
        )
        # fmt: on
