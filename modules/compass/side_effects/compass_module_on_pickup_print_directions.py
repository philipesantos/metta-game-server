from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from modules.compass.patterns.compass_directions_function_pattern import (
    CompassDirectionsFunctionPattern,
)


class CompassModuleOnPickupPrintDirections(SideEffectDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self, event: PickUpEventPattern) -> str:
        state_at_player = StateWrapperPattern(
            AtFactPattern(self.character.key, "$player_where")
        )
        directions = CompassDirectionsFunctionPattern("$player_where")
        # fmt: off
        return (
            f"(let $player_where (match &self {state_at_player.to_metta()} $player_where)\n"
            f"    {directions.to_metta()}\n"
            f")"
        )
        # fmt: on
